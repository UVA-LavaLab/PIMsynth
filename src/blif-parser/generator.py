#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: generator.py
Description: C++ code generator using bit-wise operations
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu> - BLIF-to-C parser generator code framework
Date: 2024-09-03
"""

class Generator():
    def __init__(self, parser):
        self.parser = parser
        self.dataType = "uint64_t"

    def generateCode(self):
        str = ""
        str += self.generateHeaderFile() + "\n\n"
        str += self.generateHeader()
        str += self.generateBody()
        return str

    def generateHeaderFile(self):
        return "#include <cstdint>"

    def generateHeader(self):
        str = "void "
        str += self.generateFunctionName()
        str += "(\n"
        str += self.generateInputArgs()
        str += self.generateOutputArgs()
        str += ")\n"
        return str

    def generateFunctionName(self):
        str = self.parser.moduleName
        return str

    def generateInputArgs(self):
        return ''.join(f"\t{self.dataType} {item},\n" for item in self.parser.inputsList)

    def generateOutputArgs(self):
        numOutputs = len(self.parser.outputsList)
        return ''.join(
            f"\t{self.dataType} &{item}{',' if i != numOutputs - 1 else ''}\n"
            for i, item in enumerate(self.parser.outputsList)
        )

    def generateBody(self):
        str = "{\n"
        str += self.generateTemporaryVariables()
        str += self.generateStatementSequence()
        str += "\n}\n"
        return str

    def generateTemporaryVariables(self):
        if len(self.parser.wireList) == 0:
            return ""
        variables = ', '.join(self.parser.wireList)
        return f"\t{self.dataType} {variables};\n"

    def generateStatementSequence(self):
        operations = {
            'inv1': lambda inputs: f"~{inputs[0]}",
            'and2': lambda inputs: f"({inputs[0]} & {inputs[1]})",
            'or2': lambda inputs: f"({inputs[0]} | {inputs[1]})",
            'nand2': lambda inputs: f"~({inputs[0]} & {inputs[1]})",
            'nor2': lambda inputs: f"~({inputs[0]} | {inputs[1]})",
            'xor2': lambda inputs: f"({inputs[0]} ^ {inputs[1]})",
            'xnor2': lambda inputs: f"~({inputs[0]} ^ {inputs[1]})",
        }

        result = ""
        for gate in self.parser.gatesList:
            result += f"\t{gate.outputs[0]} = "
            for key, func in operations.items():
                if gate.type.startswith(key):
                    result += f"{func(gate.inputs)};\n"
                    break
            else:
                raise ValueError(f"Unhandled gate type: {gate.type}")

        return result

