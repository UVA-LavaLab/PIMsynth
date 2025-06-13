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


class GateInfo:
    """ For passing gate information from parser to DAG """

    def __init__(self, gate_id, gate_func, inputs, outputs):
        """ Initialize """
        self.gate_id = gate_id
        self.gate_func = gate_func
        self.inputs = inputs
        self.outputs = outputs

    def __repr__(self):
        """ String representation of GateInfo """
        return f"{self.gate_func:<10} {self.gate_id:<10} | outputs: {str(self.outputs):<20} | inputs: {str(self.inputs)}"


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
    """ BLIF parser class: Parse a BLIF file """

    def __init__(self, module_name):
        """ Initialize the BLIF parser """
        self.lark_parser = Lark(BLIF_GRAMMAR, parser='lalr', transformer=BlifTransformer())
        self.parse_tree = None
        self.module_name = module_name

    def parse(self, blif_content):
        """ Parse the input BLIF file content and create DAG """
        self.parse_tree = self.lark_parser.parse(blif_content)

    def print_tree(self):
        """ Print the parse tree """
        pprint.pprint(self.parse_tree)

    def get_in_ports(self):
        """ Get input ports from the parse tree """
        assert self.parse_tree is not None
        for item in self.parse_tree.children:
            if 'inputs' in item.keys():
                return list(itertools.chain(*item['inputs']))
        return []

    def get_out_ports(self):
        """ Get output ports from the parse tree """
        assert self.parse_tree is not None
        for item in self.parse_tree.children:
            if 'outputs' in item.keys():
                return list(itertools.chain(*item['outputs']))
        return []

    def get_gate_info_list(self):
        """ Get gate info list from the parse tree """
        assert self.parse_tree is not None
        gate_info_list = []
        gate_count = 0
        for item in self.parse_tree.children:
            if isinstance(item, dict) and 'gate_name' in item:
                # Note: Revisit this part if any gate has multiple outputs in BLIF file
                args = item['arguments']
                inputs = [s for sub in args[:-1] for s in sub]  # flatten
                outputs = list(args[-1])
                gate_info = GateInfo(
                    gate_id=str(gate_count),
                    gate_func=item['gate_name'],
                    inputs=inputs,
                    outputs=outputs
                )
                gate_info_list.append(gate_info)
                gate_count += 1
        return gate_info_list

