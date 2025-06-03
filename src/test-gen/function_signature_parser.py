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

class FunctionSignatureTransformer(Transformer):
    def __init__(self):
        self.input_operands = []
        self.output_operands = []
        self.function_name = None

    def param(self, items):
        raw_type = items[0].children[0].value
        var_name = items[1].value
        is_pointer = "*" in raw_type
        base_type = raw_type.replace("*", "").strip()
        if base_type.endswith("_t"):
            base_type = base_type[:-2]

        if is_pointer:
            self.output_operands.append((var_name, base_type))
        else:
            self.input_operands.append((var_name, base_type))

    def start(self, _):
        return self.input_operands, self.output_operands, self.function_name

    def IDENTIFIER(self, token):
        if not self.function_name:
            self.function_name = str(token)
        return token


class FunctionSignatureParser:
    def __init__(self):
        self.grammar = """
            start: "void" IDENTIFIER "(" [param_list] ")"
            param_list: param ("," param)*
            param: type IDENTIFIER
            type: TYPE

            IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
            TYPE: /[a-zA-Z_][a-zA-Z0-9_]*[*]*/

            %ignore " "
        """
    def __extract_signature_block(self, golden_function_content):
        start_token = "// SIGNATURE_START"
        end_token = "// SIGNATURE_END"

        start_index = golden_function_content.find(start_token)
        end_index = golden_function_content.find(end_token)

        if start_index == -1 or end_index == -1 or start_index >= end_index:
            return None

        start_index += len(start_token)
        return golden_function_content[start_index:end_index].strip()


    def parse(self, golden_function_content):
        parser = Lark(self.grammar, parser="lalr", transformer=FunctionSignatureTransformer())
        input_operands, output_operands, function_name = \
            parser.parse(self.__extract_signature_block(golden_function_content))
        return input_operands, output_operands, function_name

