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
        self.zero = "zero"
        self.one = "one"
        self.tmpBool = "tmpBool"

    def mapPimAsmRegToPimEvalAPI(self, pimAsmReg):
        # Note: 14 registers are supported.
        # register 14 and 15 are reserved
        regMap = {
            "t0": f"{self.regFile}, 0",
            "t1": f"{self.regFile}, 1",
            "t2": f"{self.regFile}, 2",
            "t3": f"{self.regFile}, 3",
            "t4": f"{self.regFile}, 4",
            "t5": f"{self.regFile}, 5",
            "t6": f"{self.regFile}, 6",
            "s0": f"{self.regFile}, 7",
            "s1": f"{self.regFile}, 8",
            "s2": f"{self.regFile}, 9",
            "s3": f"{self.regFile}, 10",
            "s4": f"{self.regFile}, 11",
            "s5": f"{self.regFile}, 12",
            "s6": f"{self.regFile}, 13",
            "s7": f"{self.regFile}, 14",
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
        code += f"\tpimOpAAP(3, 1, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[1])}, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[2])}, {self.regFile}, 14, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[0])});\n\n"
        return code

    def handleMajInstruction(self, instruction):
        if not (instruction.opCode == "maj3"):
            return None
        code = self.generateInstructionComment(instruction)
        code += f"\tpimOpAAP(3, 1, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[1])}, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[2])}, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[3])}, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[0])});\n\n"
        return code

    def handleNotInstruction(self, instruction):
        if not (instruction.opCode == "not"):
            return None
        code = self.generateInstructionComment(instruction)
        code += f"\tpimOpAAP(1, 1, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[1])}, {self.tmpBool}, 0);\n"
        code += f"\tpimOpAAP(1, 1, pimCreateDualContactRef({self.tmpBool}), 0, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[0])});\n\n"
        return code

    def handleMoveInstruction(self, instruction):
        if not (instruction.opCode == "mv"):
            return None
        code = self.generateInstructionComment(instruction)
        code += f"\tpimOpAAP(1, 1, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[1])}, {self.tmpBool}, 0);\n"
        code += f"\tpimOpAAP(1, 1, {self.tmpBool}, 0, {self.mapPimAsmRegToPimEvalAPI(instruction.operandsList[0])});\n\n"
        return code

    def generateLogicInstruction(self, instruction):
        code = self.handleAndInstruction(instruction)
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
  PimObjId {self.zero} = pimAllocAssociated({self.firstIoPort}, PIM_BOOL);
  PimObjId {self.one} = pimAllocAssociated({self.firstIoPort}, PIM_BOOL);
  PimObjId {self.tmpBool} = pimAllocAssociated({self.firstIoPort}, PIM_BOOL);
  pimBroadcastUInt({self.zero}, 0);
  pimBroadcastUInt({self.one}, 1);\n
        """

    def generateSpecialVariablesFreeFunctions(self):
        return f"""\
  pimFree({self.regFile});
  pimFree({self.zero});
  pimFree({self.one});
  pimFree({self.tmpBool});
        """

