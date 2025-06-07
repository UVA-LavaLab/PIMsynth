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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util import *
from pimeval_code_generator_base import *

class PimEvalAPIDigitalCodeGenerator(PimEvalAPICodeGeneratorBase):
    def mapPimAsmRegToPimEvalAPI(self, pimAsmReg):
        regMap = {
            "t0": "PIM_RREG_R1",
            "t1": "PIM_RREG_R2",
            "t2": "PIM_RREG_R3",
            "t3": "PIM_RREG_R4",
            "t4": "PIM_RREG_R5",
            "t5": "PIM_RREG_R6",
            "t6": "PIM_RREG_R7",
            "s0": "PIM_RREG_R8",
            "s1": "PIM_RREG_R9",
            "s2": "PIM_RREG_R10",
            "s3": "PIM_RREG_R11",
            "s4": "PIM_RREG_R12",
            "s5": "PIM_RREG_R13",
            "s6": "PIM_RREG_R14",
            "s7": "PIM_RREG_R15",
            "s8": "PIM_RREG_R16",
            "s9": "PIM_RREG_R17",
            "s10": "PIM_RREG_R18",
            "s11": "PIM_RREG_R19",
        }
        if pimAsmReg in regMap:
            return regMap[pimAsmReg]
        else:
            raise ValueError(f"Invalid register: {pimAsmReg}")

    def mapPimAsmOpCodeToPimEvalAPI(self, pimOpCode):
        opCodeMap = {
            "not": "pimOpNot",
            "mv": "pimOpMove",
            "and": "pimOpAnd",
            "or": "pimOpOr",
            "xor": "pimOpXor",
            "nand": "pimOpNand",
            "nor": "pimOpNor",
            "xnor": "pimOpXnor",
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
        code += f"\tpimOpMove({self.firstIoPort}, PIM_RREG_SA, {self.mapPimAsmRegToPimEvalAPI(destinationOperand)});\n\n"

        return code

    def generateWriteInstruction(self, instruction):
        code = self.generateInstructionComment(instruction)

        sourceOperand = instruction.operandsList[0]
        code += f"\tpimOpMove({self.firstIoPort}, {self.mapPimAsmRegToPimEvalAPI(sourceOperand)}, PIM_RREG_SA);\n"

        destinationOperand = self.formatOperand(instruction.operandsList[1])
        code += f"\tpimOpWriteSaToRow({destinationOperand});\n\n"

        return code

    def generateLogicalInstructionOperands(self, operandsList):
        reorderedOperandList = operandsList[1:] + [operandsList[0]]
        functionOperands = list(map(self.mapPimAsmRegToPimEvalAPI, reorderedOperandList))
        code = f"{concatenateListElements(functionOperands)}"
        return code

    def handleOneInstruction(self, instruction):
        if not (instruction.opCode == "one"):
            return None
        code = f"\t// one {instruction.operandsList[0]} (Line: {instruction.line})\n"
        code += f"\tpimOpSet({self.firstIoPort}, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[0])}, true);\n\n"
        return code

    def handleZeroInstruction(self, instruction):
        if not (instruction.opCode == "zero"):
            return None
        code = f"\t// zero {instruction.operandsList[0]} (Line: {instruction.line})\n"
        code += f"\tpimOpSet({self.firstIoPort}, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[0])}, false);\n\n"
        return code

    def generateLogicInstruction(self, instruction):
        code = self.handleOneInstruction(instruction)
        if code != None:
            return code
        code = self.handleZeroInstruction(instruction)
        if code != None:
            return code
        code = self.generateInstructionComment(instruction)
        pimEvalFunctionName = self.mapPimAsmOpCodeToPimEvalAPI(instruction.opCode)
        code += f"\t{pimEvalFunctionName}({self.firstIoPort}, {self.generateLogicalInstructionOperands(instruction.operandsList)});\n\n"
        return code

    def generateSpecialVariables(self):
        return ""

    def generateSpecialVariablesFreeFunctions(self):
        return ""

