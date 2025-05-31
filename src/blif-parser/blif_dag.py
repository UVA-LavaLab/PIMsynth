#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: blif_dag.py
Description: DAG representation for BLIF translator
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Author: Deyaun Guo <guodeyuan@gmail.com>
Date: 2025-05-28
"""

import json
from networkx.readwrite import json_graph
from pyvis.network import Network
import networkx as nx

class GateNode:
    def __init__(self, gateId, gateType, inputs, outputs):
        self.id = gateId
        self.type = gateType
        self.inputs = inputs
        self.outputs = outputs

    def __repr__(self):
        return f"{self.type:<10} | outputs: {str(self.outputs):<30} | inputs: {str(self.inputs)}"

class Dag:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.signalToGateOutput = {}
        self.gateInfo = {}

    def addGate(self, gateNode: GateNode):
        gateId = gateNode.id
        self.graph.add_node(gateId)
        self.gateInfo[gateId] = gateNode

        for inputSignal in gateNode.inputs:
            if inputSignal in self.signalToGateOutput:
                sourceGateId = self.signalToGateOutput[inputSignal].id
                self.graph.add_edge(sourceGateId, gateId)

        for outputSignal in gateNode.outputs:
            self.signalToGateOutput[outputSignal] = gateNode

    def __repr__(self):
        code = ""
        for gate in self.getTopologicallySortedGates():
            code += gate.__repr__() + "\n"
        return code

    def getTopologicallySortedGates(self):
        return [self.gateInfo[gateId] for gateId in nx.topological_sort(self.graph)]

def convertTreeToDag(tree):
    dag = Dag()
    gateCounter = 0
    for item in tree.children:
        if isinstance(item, dict) and 'gate_name' in item:
            gateType = item['gate_name']
            args = item['arguments']
            inputs = [s for sub in args[:-1] for s in sub]
            outputs = [s for s in args[-1]]
            gateNode = GateNode(gateId=gateCounter, gateType=gateType, inputs=inputs, outputs=outputs)
            dag.addGate(gateNode)
            gateCounter += 1
    return dag


def saveDagAsJson(dag, filePath):
    # Embed gateInfo into node attributes
    for gateId, gate in dag.gateInfo.items():
        dag.graph.nodes[gateId]["type"] = gate.type
        dag.graph.nodes[gateId]["inputs"] = gate.inputs
        dag.graph.nodes[gateId]["outputs"] = gate.outputs

    # Export graph with embedded attributes
    data = json_graph.node_link_data(dag.graph, edges="links")

    with open(filePath, "w") as f:
        json.dump(data, f, indent=2)


def loadDagFromJson(filePath):
    with open(filePath) as f:
        data = json.load(f)

    dag = Dag()
    dag.graph = json_graph.node_link_graph(data, edges="links")

    # Rebuild gateInfo and signalToGateOutput
    for nodeId, attrs in dag.graph.nodes(data=True):
        gate = GateNode(
            gateId=nodeId,
            gateType=attrs.get("type", "unknown"),
            inputs=attrs.get("inputs", []),
            outputs=attrs.get("outputs", [])
        )
        dag.gateInfo[nodeId] = gate
        for output in gate.outputs:
            dag.signalToGateOutput[output] = gate

    return dag

def drawInteractiveCircuit(dag, outputFile="circuit.html"):
    net = Network(height='800px', width='100%', directed=True, notebook=False, filter_menu=True, cdn_resources='remote')
    graph = dag.graph

    for nodeId, data in graph.nodes(data=True):
        gateType = data.get('type', 'unknown')
        outputs = ', '.join(data.get('outputs', []))
        label = f"{gateType}\n{outputs}"
        net.add_node(nodeId, label=label, shape="box", color="#AED6F1")

    for u, v, edge_data in graph.edges(data=True):
        label = edge_data.get('label')
        if label is None:
            fromSignals = set(graph.nodes[u].get('outputs', []))
            toSignals = set(graph.nodes[v].get('inputs', []))
            common = fromSignals & toSignals
            label = ', '.join(common) if common else ''
        net.add_edge(u, v, label=label)

    net.show_buttons(filter_=['physics'])
    net.show(outputFile)
    print(f"Interactive graph saved to: {outputFile}")

