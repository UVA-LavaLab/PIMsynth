#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: fanout_normalizer.py
Description: Eliminates multi-fanout wires by inserting dedicated copy gates for all but one consumer.
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Date: 2025-05-08
"""

from blif_parser import *
from typing import Dict, List
from dag_transformer_base import DagTransformer
import networkx as nx

def removeTrailingStars(strings):
    return [s[:-1] if s.endswith('*') else s for s in strings]

def removeTrailingStarsFromGatesList(gatesList):
    for i in range(len(gatesList)):
        gatesList[i].inputs = removeTrailingStars(gatesList[i].inputs)
    return gatesList

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
            isInvGate = (producerGate.type == "inv1")
            isCopyGate = (producerGate.type == "copy")
            hasReusableInputs = (not (isInvGate or isCopyGate))
            originalConsumerId = consumers[0]
            remainingConsumerIds = consumers[1:]
            if hasReusableInputs:
                remainingConsumerIds = self.replaceWithInputs(dag, signal, producerId, remainingConsumerIds)
                self.insertCopyNodes(dag, signal, producerId, remainingConsumerIds, originalConsumerId)
            elif isInvGate:
                self.insertCopyNodes(dag, signal, producerId, remainingConsumerIds, originalConsumerId)
            else:
                raise Exception("Error: Unexpected behaivior happened.")

        return dag

    def replaceWithInputs(self, dag, signal: str, producerId: str, consumerIds: List[str]):
        producerGate = dag.gateInfo[producerId]
        inputs = producerGate.inputs
        reusableInputs = []
        for x in inputs:
            if not "*" in x:
                reusableInputs.append(x)

        n = min(len(reusableInputs), len(consumerIds))
        for idx in range(n):
            newInputSignal = reusableInputs[idx]
            consumerId = consumerIds[idx]
            if dag.graph.has_edge(producerId, consumerId):
                dag.graph.remove_edge(producerId, consumerId)
            dag.graph.add_edge(producerId, consumerId, label='Fake') # Fake edge to maintain topological sort

            consumerGate = dag.gateInfo[consumerId]
            consumerGate.inputs = [
                newInputSignal + "*" if s == signal else s
                for s in consumerGate.inputs
            ]
            dag.gateInfo[consumerId] = consumerGate

        remainingConsumerIds = consumerIds[n:]
        return remainingConsumerIds

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

    def insertCopyNodes(self, dag, signal: str, producerId: str, consumerIds: List[str], originalConsumerId: str):
        lastSignal = signal
        lastProducerId = producerId
        lastConsumerId = originalConsumerId

        for consumerId in consumerIds:
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

