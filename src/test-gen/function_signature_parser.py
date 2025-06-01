#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: main.py
Description: Function signature parser using Lark to extract input and output operands.
             Automatically strips '_t' from type names and classifies pointers as outputs.
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Date: 2025-04-05
"""

from lark import Lark, Transformer

class OperandExtractor(Transformer):
    def __init__(self):
        self.inputOperands = []
        self.outputOperands = []
        self.functionName = None

    def param(self, items):
        raw_type = items[0].children[0].value
        var_name = items[1].value
        is_pointer = "*" in raw_type
        base_type = raw_type.replace("*", "").strip()
        if base_type.endswith("_t"):
            base_type = base_type[:-2]

        if is_pointer:
            self.outputOperands.append((var_name, base_type))
        else:
            self.inputOperands.append((var_name, base_type))

    def start(self, _):
        return self.inputOperands, self.outputOperands, self.functionName

    def IDENTIFIER(self, token):
        if not self.functionName:
            self.functionName = str(token)
        return token


class FunctionSignatureParser:
    def __init__(self, signature=None):
        self.grammar = """
            start: "void" IDENTIFIER "(" [param_list] ")"
            param_list: param ("," param)*
            param: type IDENTIFIER
            type: TYPE

            IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
            TYPE: /[a-zA-Z_][a-zA-Z0-9_]*[*]*/

            %ignore " "
        """

    def parse(self, signature):
        parser = Lark(self.grammar, parser="lalr", transformer=OperandExtractor())
        inputOperands, outputOperands, functionName = parser.parse(signature)
        return inputOperands, outputOperands, functionName

