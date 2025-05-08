#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: parser.py
Description: BLIF parser
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu> - BLIF-to-C parser generator code framework
Author: Deyuan Guo <guodeyuan@gmail.com> - Support bus inputs and outputs; Support backslash; Support mux/maj
Date: 2024-09-03
"""

from lark import Lark, Transformer, v_args
import itertools
import pprint
import networkx as nx

# Define the Transformer class
class CircuitTransformer(Transformer):
    def header(self, items):
        return {"header": items[0]}

    def model(self, items):
        return {"model": items[0]}

    def inputs(self, items):
        return {"inputs": list(items)}

    def outputs(self, items):
        return {"outputs": list(items)}

    def gate(self, items):
        gate_name = items[0]
        arguments = items[1].children
        return {"gate_name": gate_name, "arguments": arguments}

    def end(self, items):
        return {"end": ".end"}

    def argument(self, items):
        return items

    def input_list(self, items):
        return items

    def output_list(self, items):
        return items

    def IDENTIFIER(self, item):
        return str(item)

    def GATE_NAME(self, item):
        return str(item)

    def PATH(self, item):
        return str(item)

    def COMMENT(self, item):
        return str(item)

# Define the grammar
circuitGrammar = r"""
    start: header model inputs outputs gate+ end

    header: COMMENT
    model: ".model" PATH
    inputs: ".inputs" input_list
    outputs: ".outputs" output_list
    gate: ".gate" GATE_NAME arguments
    end: ".end"

    input_list: IDENTIFIER (IDENTIFIER)*
    output_list: IDENTIFIER (IDENTIFIER)*

    arguments: argument (argument)*
    argument: "a=" IDENTIFIER
            | "b=" IDENTIFIER
            | "c=" IDENTIFIER
            | "s=" IDENTIFIER
            | "O=" IDENTIFIER

    COMMENT: /#[^\n]*/
    PATH: /[a-zA-Z0-9\/_.-]+/
    IDENTIFIER: /[a-zA-Z0-9_\[\]]+/
    GATE_NAME: /[a-zA-Z0-9]+/

    %import common.WS
    %ignore WS
    %ignore /\\/


"""

class GateNode:
    def __init__(self, gateId, gateType, inputs, outputs):
        self.id = gateId
        self.type = gateType
        self.inputs = inputs
        self.outputs = outputs

    def __repr__(self):
        return f"{self.type}_{self.id}, inputs: {self.inputs}, outputs: {self.outputs}"

class Dag:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.signalToGateOutput = {}

    def addGate(self, gateNode: GateNode):
        self.graph.add_node(gateNode, label=gateNode.type)
        # For each input, if it was output by another gate, create an edge
        for inputSignal in gateNode.inputs:
            if inputSignal in self.signalToGateOutput:
                sourceGate = self.signalToGateOutput[inputSignal]
                self.graph.add_edge(sourceGate, gateNode)
        # Register this gate as the source for its output signal(s)
        for outputSignal in gateNode.outputs:
            self.signalToGateOutput[outputSignal] = gateNode

    def getTopologicallySortedGates(self):
        return list(nx.topological_sort(self.graph))

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

class Parser():
    def __init__(self, moduleName="TestModule"):
        # Create the Lark parser
        self.larkParser = Lark(circuitGrammar, parser='lalr', transformer=CircuitTransformer())
        self.parseTree = None
        self.gatesList = []
        self.wireList = []
        self.inputsList = []
        self.outputsList = []
        self.moduleName = moduleName

    def parse(self, inStr):
        self.parseTree = self.larkParser.parse(inStr)
        self.dag = convertTreeToDag(self.parseTree)
        self.gatesList = self.dag.getTopologicallySortedGates()
        self.getPortList()
        self.getWireList()

    def getWireList(self):
        for gate in self.gatesList:
            if 'new' in gate.outputs[0]:
                self.wireList.append(gate.outputs[0])

    def getPortList(self):
        for item in self.parseTree.children:
            if 'inputs' in item.keys():
                self.inputsList = list(itertools.chain(*item['inputs']))
            if 'outputs' in item.keys():
                self.outputsList = list(itertools.chain(*item['outputs']))

    def getName(self):
        self.moduleName = self.parseTree['name']

    def printTree(self):
        pprint.pprint(self.parseTree)

    def extractListFromKey(self, objList, key):
        returnList = []
        for obj in objList:
            if obj['type'] == key:
                returnList.append(obj)
        return returnList

