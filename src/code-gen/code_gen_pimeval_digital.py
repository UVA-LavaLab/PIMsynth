#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: digital_pimeval_code_generator.py
Description: bit-serial code generator in PIMeval API for the digital PIM
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu> - RISCV-to-BITSERIAL code generator framework
Date: 2025-05-17
"""

import re
import math
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
from util import *
from code_gen_pimeval_base import PimEvalAPICodeGeneratorBase


class PimEvalAPIDigitalCodeGenerator(PimEvalAPICodeGeneratorBase):
    def mapRegToPimEvalAPI(self, reg):
        """Map generic register name rN to PIMeval API constant PIM_RREG_R{N+1}."""
        if reg.startswith('r') and reg[1:].isdigit():
            return f"PIM_RREG_R{int(reg[1:]) + 1}"
        raise ValueError(f"Invalid register: {reg}")

    def mapOpCodeToPimEvalAPI(self, pimOpCode):
        opCodeMap = {
            "inv1": "pimOpNot",
            "mv": "pimOpMove",
            "and2": "pimOpAnd",
            "or2": "pimOpOr",
            "xor2": "pimOpXor",
            "nand2": "pimOpNand",
            "nor2": "pimOpNor",
            "xnor2": "pimOpXnor",
            "maj3": "pimOpMaj",
            "mux2": "pimOpSel",
            "zero": "pimOpSet",
            "one": "pimOpSet",
        }
        if pimOpCode in opCodeMap:
            return opCodeMap[pimOpCode]
        else:
            raise ValueError(f"Invalid PIM opcode: {pimOpCode}")

    def generateReadInstruction(self, instruction):
        code = self.generateInstructionComment(instruction)

        sourceOperand = self.formatOperand(instruction.operandsList[1])
        code += f"\tpimOpReadRowToSa({sourceOperand});\n"

        destinationOperand = instruction.operandsList[0]
        code += f"\tpimOpMove({self.firstIoPort}, PIM_RREG_SA, {self.mapRegToPimEvalAPI(destinationOperand)});\n\n"

        return code

    def generateWriteInstruction(self, instruction):
        code = self.generateInstructionComment(instruction)

        sourceOperand = instruction.operandsList[0]
        code += f"\tpimOpMove({self.firstIoPort}, {self.mapRegToPimEvalAPI(sourceOperand)}, PIM_RREG_SA);\n"

        destinationOperand = self.formatOperand(instruction.operandsList[1])
        code += f"\tpimOpWriteSaToRow({destinationOperand});\n\n"

        return code

    def generateLogicalInstructionOperands(self, operandsList):
        reorderedOperandList = operandsList[1:] + [operandsList[0]]
        functionOperands = list(map(self.mapRegToPimEvalAPI, reorderedOperandList))
        code = f"{concatenateListElements(functionOperands)}"
        return code

    def handleOneInstruction(self, instruction):
        if not (instruction.opCode == "one"):
            return None
        code = f"\t// one {instruction.operandsList[0]} (Line: {instruction.line})\n"
        code += f"\tpimOpSet({self.firstIoPort}, {self.mapRegToPimEvalAPI(instruction.operandsList[0])}, true);\n\n"
        return code

    def handleZeroInstruction(self, instruction):
        if not (instruction.opCode == "zero"):
            return None
        code = f"\t// zero {instruction.operandsList[0]} (Line: {instruction.line})\n"
        code += f"\tpimOpSet({self.firstIoPort}, {self.mapRegToPimEvalAPI(instruction.operandsList[0])}, false);\n\n"
        return code

    def generateLogicInstruction(self, instruction):
        code = self.handleOneInstruction(instruction)
        if code != None:
            return code
        code = self.handleZeroInstruction(instruction)
        if code != None:
            return code
        code = self.generateInstructionComment(instruction)
        pimEvalFunctionName = self.mapOpCodeToPimEvalAPI(instruction.opCode)
        code += f"\t{pimEvalFunctionName}({self.firstIoPort}, {self.generateLogicalInstructionOperands(instruction.operandsList)});\n\n"
        return code

    def generateSpecialVariables(self):
        return ""

    def generateSpecialVariablesFreeFunctions(self):
        return ""

