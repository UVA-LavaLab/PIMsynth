#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: blif_parser.py
Description: BLIF parser
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu> - BLIF-to-C parser generator code framework
Author: Deyuan Guo <guodeyuan@gmail.com> - Support bus inputs and outputs; Support backslash; Support mux/maj
Date: 2024-09-03
"""

from lark import Lark, Transformer, v_args
import itertools
import pprint
import networkx as nx
from blif_dag import *


# Define the BLIF Transformer class for Lark
class BlifTransformer(Transformer):
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


# Define the BLIF grammar
BlifGrammar = r"""
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

class BlifParser:
    """ BLIF parser class: Convert a BLIF file to a DAG representation """

    def __init__(self, moduleName):
        """ Initialize the BLIF parser """
        self.larkParser = Lark(BlifGrammar, parser='lalr', transformer=BlifTransformer())
        self.parseTree = None
        self.moduleName = moduleName

    def parse(self, inStr):
        """ Parse the input BLIF file content and create DAG """
        self.parseTree = self.larkParser.parse(inStr)
        success, dag = self.convertTreeToDag()
        return success, dag

    def printTree(self):
        """ Print the parse tree """
        pprint.pprint(self.parseTree)

    def convertTreeToDag(self):
        """ Convert parse tree to DAG """
        success = True
        dag = Dag()
        dag.module_name = self.moduleName

        # Handle gates
        gateCounter = 0
        for item in self.parseTree.children:
            if isinstance(item, dict) and 'gate_name' in item:
                gateType = item['gate_name']
                args = item['arguments']
                inputs = [s for sub in args[:-1] for s in sub]
                outputs = [s for s in args[-1]]
                gateNode = GateNode(gateId=gateCounter, gateType=gateType, inputs=inputs, outputs=outputs)
                dag.addGate(gateNode)
                gateCounter += 1

        # Handle in/out parts
        for item in self.parseTree.children:
            if 'inputs' in item.keys():
                dag.inPortList = list(itertools.chain(*item['inputs']))
            if 'outputs' in item.keys():
                dag.outPortList = list(itertools.chain(*item['outputs']))

        # Temp: Set gate list and wire list
        dag.gateList = dag.getGateList()
        dag.wireList = dag.getWireList()

        return (success, dag) if success else (False, None)

