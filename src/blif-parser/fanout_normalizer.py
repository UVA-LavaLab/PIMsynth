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
            fanout = len(consumers)
            if fanout <= 1:
                continue

            producerId = signalProducers.get(signal)
            if producerId is None:
                continue

            producerGate = dag.gateInfo[producerId]
            ic = len(producerGate.inputs)

            if fanout <= 1 + ic and not (producerGate.type == "inv1" or producerGate.type == "copy"):
                self.replaceWithInputs(dag, signal, producerId, consumers)
            else:
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

    def replaceWithInputs(self, dag, signal: str, producerId: str, consumerIds: List[str]):
        producerGate = dag.gateInfo[producerId]
        inputs = producerGate.inputs

        originalConsumerId = consumerIds[0]
        remainingConsumerIds = consumerIds[1:]

        for idx, consumerId in enumerate(remainingConsumerIds):
            newInputSignal = inputs[idx]
            if dag.graph.has_edge(producerId, consumerId):
                dag.graph.remove_edge(producerId, consumerId)
            dag.graph.add_edge(producerId, consumerId, label='Fake') # Fake edge to maintain topological sort

            consumerGate = dag.gateInfo[consumerId]
            consumerGate.inputs = [
                newInputSignal if s == signal else s
                for s in consumerGate.inputs
            ]
            dag.gateInfo[consumerId] = consumerGate

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

            dag.addGate(copyNode)
            dag.graph.add_edge(lastProducerId, copyNodeId)
            dag.graph.add_edge(copyNodeId, lastConsumerId, label='Fake')
            dag.graph.add_edge(copyNodeId, consumerId)

            consumerGate = dag.gateInfo[consumerId]
            consumerGate.inputs = [
                newOutputSignal if s == signal else s
                for s in consumerGate.inputs
            ]
            dag.gateInfo[consumerId] = consumerGate

            lastSignal = newOutputSignal
            lastProducerId = copyNodeId
            lastConsumerId = consumerId

