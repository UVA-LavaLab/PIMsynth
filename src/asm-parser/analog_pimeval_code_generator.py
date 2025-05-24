#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: analog_pimeval_code_generator.py
Description: bit-serial code generator in PIMeval API for the analog PIM
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

class PimEvalAPIAnalogCodeGenerator(PimEvalAPICodeGeneratorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.regFile = "regFile"
        self.regFileNot = self.regFile + "Not"
        self.zero = "zero"
        self.one = "one"

    def mapPimAsmRegToPimEvalAPI(self, pimAsmReg, isInverted=False):
        # Note: 14 registers are supported.
        # register 14 and 15 are reserved
        if isInverted:
            regFile = self.regFileNot
        else:
            regFile = self.regFile
        regMap = {
            "t0": f"{regFile}, 0",
            "t1": f"{regFile}, 1",
            "t2": f"{regFile}, 2",
            "t3": f"{regFile}, 3",
            "t4": f"{regFile}, 4",
            "t5": f"{regFile}, 5",
            "t6": f"{regFile}, 6",
            "s0": f"{regFile}, 7",
            "s1": f"{regFile}, 8",
            "s2": f"{regFile}, 9",
            "s3": f"{regFile}, 10",
            "s4": f"{regFile}, 11",
            "s5": f"{regFile}, 12",
            "s6": f"{regFile}, 13",
        }
        if pimAsmReg in regMap:
            return regMap[pimAsmReg]
        else:
            raise ValueError(f"Invalid register: {pimAsmReg}")


    def generateReadInstruction(self, instruction):
        code = self.generateInstructionComment(instruction)
        sourceOperand = self.formatOperand(instruction.operandsList[1])
        destinationOperand = instruction.operandsList[0]
        code += f"\tpimOpAAP(1, 1, {sourceOperand}, {self.mapPimAsmRegToPimEvalAPI(destinationOperand)});\n\n"
        return code

    def generateWriteInstruction(self, instruction):
        code = self.generateInstructionComment(instruction)
        sourceOperand = instruction.operandsList[0]
        destinationOperand = self.formatOperand(instruction.operandsList[1])
        code += f"\tpimOpAAP(1, 1, {self.mapPimAsmRegToPimEvalAPI(sourceOperand)}, {destinationOperand});\n\n"
        return code

    def handleAndInstruction(self, instruction):
        if not (instruction.opCode == "and"):
            return None
        code = self.generateInstructionComment(instruction)
        code += f"\tpimOpAAP(1, 1, {self.zero}, 0, {self.regFile}, 14);\n"
        if instruction.operandsList[0] in instruction.operandsList[1:]:
            code += f"\tpimOpAP(3, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[1])}, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[2])}, {self.regFile}, 14);\n\n"
        else:
            code += f"\tpimOpAAP(3, 1, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[1])}, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[2])}, {self.regFile}, 14, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[0])});\n\n"
        return code

    def handleOrInstruction(self, instruction):
        if not (instruction.opCode == "or"):
            return None
        code = self.generateInstructionComment(instruction)
        code += f"\tpimOpAAP(1, 1, {self.one}, 0, {self.regFile}, 14);\n"
        if instruction.operandsList[0] in instruction.operandsList[1:]:
            code += f"\tpimOpAP(3, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[1])}, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[2])}, {self.regFile}, 14);\n\n"
        else:
            code += f"\tpimOpAAP(3, 1, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[1])}, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[2])}, {self.regFile}, 14, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[0])});\n\n"
        return code

    def handleMajInstruction(self, instruction):
        if not (instruction.opCode == "maj3"):
            return None
        code = self.generateInstructionComment(instruction)
        if instruction.operandsList[0] in instruction.operandsList[1:]:
            code += f"\tpimOpAP(3, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[1])}, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[2])}, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[3])});\n\n"
        else:
            code += f"\tpimOpAAP(3, 1, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[1])}, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[2])}, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[3])}, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[0])});\n\n"
        return code

    def handleNotInstruction(self, instruction):
        if not (instruction.opCode == "not"):
            return None
        code = self.generateInstructionComment(instruction)
        if instruction.operandsList[0] in instruction.operandsList[1:]:
            code += f"\tpimOpAAP(1, 1, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[1], isInverted=True)}, {self.regFile}, 14);\n"
            code += f"\tpimOpAAP(1, 1, {self.regFile}, 14, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[0])});\n\n"
        else:
            code += f"\tpimOpAAP(1, 1, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[1], isInverted=True)}, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[0])});\n\n"
        return code

    def handleMoveInstruction(self, instruction):
        if not (instruction.opCode == "mv"):
            return None
        code = self.generateInstructionComment(instruction)
        if instruction.operandsList[0] == instruction.operandsList[1]:
            pass
        else:
            code += f"\tpimOpAAP(1, 1, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[1])}, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[0])});\n\n"
        return code

    def generateLogicInstruction(self, instruction):
        code = self.handleAndInstruction(instruction)
        if code != None:
            return code
        code = self.handleOrInstruction(instruction)
        if code != None:
            return code
        code = self.handleMajInstruction(instruction)
        if code != None:
            return code
        code = self.handleNotInstruction(instruction)
        if code != None:
            return code
        code = self.handleMoveInstruction(instruction)
        if code != None:
            return code
        raise NotImplementedError(f"Error: instruction {instruction.opCode} is not implemented.")

    def generateSpecialVariables(self):
        return f"""\
  PimObjId {self.regFile} = pimAllocAssociated({self.firstIoPort}, PIM_UINT16);
  PimObjId {self.regFileNot} = pimCreateDualContactRef({self.regFile});
  PimObjId {self.zero} = pimAllocAssociated({self.firstIoPort}, PIM_BOOL);
  PimObjId {self.one} = pimAllocAssociated({self.firstIoPort}, PIM_BOOL);
  pimBroadcastUInt({self.zero}, 0);
  pimBroadcastUInt({self.one}, 1);\n
        """

    def generateSpecialVariablesFreeFunctions(self):
        return f"""\
  pimFree({self.regFile});
  pimFree({self.zero});
  pimFree({self.one});
        """

