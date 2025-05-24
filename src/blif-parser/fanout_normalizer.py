#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: fanout_normalizer.py
Description: Eliminates multi-fanout wires by inserting dedicated copy gates for all but one consumer.
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Date: 2025-05-08
"""

from parser import *
from typing import Dict, List
from dag_transformer_base import DagTransformer
import networkx as nx


class FanoutNormalizer(DagTransformer):
    def __init__(self):
        self.copyCounter = 0
        self.newWires = []

    def apply(self, dag):
        signalConsumers: Dict[str, List[str]] = self.getSignalConsumers(dag)
        signalProducers: Dict[str, str] = self.getSignalProducers(dag)

        for signal, consumers in signalConsumers.items():
            if len(consumers) <= 1:
                continue

            producerId = signalProducers.get(signal)
            if producerId is None:
                continue

            self.insertCopyNodes(dag, signal, producerId, consumers)

        return dag

    def getSignalConsumers(self, dag) -> Dict[str, List[str]]:
        consumers: Dict[str, List[str]] = {}
        for gateId in dag.graph.nodes:
            gate = dag.gateInfo[gateId]
            for signal in gate.inputs:
                consumers.setdefault(signal, []).append(gateId)
        return consumers

    def getSignalProducers(self, dag) -> Dict[str, str]:
        producers: Dict[str, str] = {}
        for gateId in dag.graph.nodes:
            gate = dag.gateInfo[gateId]
            for signal in gate.outputs:
                producers[signal] = gateId
        return producers

    def insertCopyNodes(self, dag, signal: str, producerId: str, consumerIds: List[str]):
        originalConsumerId = consumerIds[0]
        remainingConsumerIds = consumerIds[1:]

        lastSignal = signal
        lastProducerId = producerId
        lastConsumerId = originalConsumerId

        for consumerId in remainingConsumerIds:
            if dag.graph.has_edge(producerId, consumerId):
                dag.graph.remove_edge(producerId, consumerId)

            newOutputSignal = f"{signal}_copy_{self.copyCounter}"
            copyNodeId = f"copy_{self.copyCounter}"
            copyNode = GateNode(
                gateId=copyNodeId,
                gateType="copy",
                inputs=[lastSignal],
                outputs=[newOutputSignal]
            )
            self.copyCounter += 1
            self.newWires.append(newOutputSignal)

            # Add new gate to DAG
            dag.addGate(copyNode)

            # Add real edge from previous copy (or original) to the new copy
            dag.graph.add_edge(lastProducerId, copyNodeId)

            # Add fake edge for topological order maintenance
            dag.graph.add_edge(copyNodeId, lastConsumerId)

            # Add edge to current consumer
            dag.graph.add_edge(copyNodeId, consumerId)

            # Update consumer's input
            consumerGate = dag.gateInfo[consumerId]
            consumerGate.inputs = [
                newOutputSignal if s == signal else s
                for s in consumerGate.inputs
            ]

            # Update for next iteration
            lastSignal = newOutputSignal
            lastProducerId = copyNodeId
            lastConsumerId = consumerId

