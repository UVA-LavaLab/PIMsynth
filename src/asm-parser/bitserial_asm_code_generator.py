#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: generator.py
Description: bit-serial code generator in assembly format
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu> - RISCV-to-BITSERIAL code generator framework
Date: 2025-05-17
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util import *

class bitSerialAsmCodeGenerator:
    def __init__(self, instructionSequence):
        self.instructionSequence = instructionSequence

    def generateAsmInstruction(self, instruction):
        return f"{instruction.opCode} {concatenateListElements(instruction.operandsList)} # (Line: {instruction.line})\n"

    def generateCode(self):
        code = ""
        for instruction in self.instructionSequence:
            code += self.generateAsmInstruction(instruction)
        return code

