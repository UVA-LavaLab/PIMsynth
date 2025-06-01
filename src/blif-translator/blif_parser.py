#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: blif_parser.py
Description: BLIF parser
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu> - BLIF-to-C parser generator code framework
Author: Deyuan Guo <guodeyuan@gmail.com> - Support bus inputs and outputs; Support backslash; Support mux/maj
Date: 2024-09-03
"""

import itertools
import pprint
from lark import Lark, Transformer
from blif_dag import Dag, GateNode


class BlifTransformer(Transformer):
    """ BLIF Transformer class for Lark parsing """

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
BLIF_GRAMMAR = r"""
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

    def __init__(self, module_name):
        """ Initialize the BLIF parser """
        self.lark_parser = Lark(BLIF_GRAMMAR, parser='lalr', transformer=BlifTransformer())
        self.parse_tree = None
        self.module_name = module_name

    def parse(self, blif_content):
        """ Parse the input BLIF file content and create DAG """
        self.parse_tree = self.lark_parser.parse(blif_content)
        return self.convert_tree_to_dag()

    def print_tree(self):
        """ Print the parse tree """
        pprint.pprint(self.parse_tree)

    def convert_tree_to_dag(self):
        """ Convert parse tree to DAG """
        dag = Dag()
        dag.module_name = self.module_name

        # Handle in/out ports
        for item in self.parse_tree.children:
            if 'inputs' in item.keys():
                in_ports = list(itertools.chain(*item['inputs']))
                dag.set_in_ports(in_ports)
            if 'outputs' in item.keys():
                out_ports = list(itertools.chain(*item['outputs']))
                dag.set_out_ports(out_ports)

        # Handle gates
        gate_count = 0
        for item in self.parse_tree.children:
            if isinstance(item, dict) and 'gate_name' in item:
                gate_func = item['gate_name']
                args = item['arguments']
                inputs = [s for sub in args[:-1] for s in sub]
                outputs = list(args[-1])
                gate = GateNode(gate_id=gate_count, gate_func=gate_func, inputs=inputs, outputs=outputs)
                dag.add_gate(gate)
                gate_count += 1

        # Temp: Track gate list and wire list separately for now
        dag.gate_list = dag.get_gate_list()
        dag.wire_list = dag.get_wire_list()

        return dag
