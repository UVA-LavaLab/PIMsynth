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
        signalConsumers: Dict[str, List[GateNode]] = self.getSignalConsumers(dag)
        signalProducers: Dict[str, GateNode] = self.getSignalProducers(dag)

        for signal, consumers in signalConsumers.items():
            if len(consumers) <= 1:
                continue

            producer = signalProducers.get(signal)
            if producer is None:
                continue

            self.insertCopyNodes(dag, signal, producer, consumers)

        return dag

    def getSignalConsumers(self, dag) -> Dict[str, List[GateNode]]:
        consumers: Dict[str, List[GateNode]] = {}
        for node in dag.graph.nodes:
            if hasattr(node, 'inputs'):
                for signal in node.inputs:
                    consumers.setdefault(signal, []).append(node)
        return consumers

    def getSignalProducers(self, dag) -> Dict[str, GateNode]:
        producers: Dict[str, GateNode] = {}
        for node in dag.graph.nodes:
            if hasattr(node, 'outputs'):
                for signal in node.outputs:
                    producers[signal] = node
        return producers

    def insertCopyNodes(self, dag, signal: str, producer: GateNode, consumers: List[GateNode]):
        # Identify the original consumer as the first one in the list
        originalConsumer = consumers[0]
        remainingConsumers = consumers[1:]

        for consumer in remainingConsumers:
            if dag.graph.has_edge(producer, consumer):
                dag.graph.remove_edge(producer, consumer)

            newOutputSignal = f"{signal}_copy_{self.copyCounter}"
            copyNode = GateNode(
                gateId=f"copy_{self.copyCounter}",
                gateType="copy",
                inputs=[signal],
                outputs=[newOutputSignal]
            )
            self.newWires.append(newOutputSignal)
            self.copyCounter += 1

            dag.graph.add_node(copyNode, label=copyNode.type)
            dag.graph.add_edge(producer, copyNode)        # Real data dependency
            dag.graph.add_edge(copyNode, consumer)        # Real data dependency
            dag.graph.add_edge(copyNode, originalConsumer)  # Fake edge to enforce topological order

            consumer.inputs = [
                newOutputSignal if s == signal else s
                for s in consumer.inputs
            ]

