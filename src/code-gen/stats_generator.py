#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: stats_generator.py
Description: bit-serial code stats genrator - for example: #R/#W/#L: 32/16/18
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu> - RISCV-to-BITSERIAL code generator framework
Date: 2025-05-17
"""

class StatsGenerator:
    def __init__(self, instructionSequence):
        self.instructionSequence = instructionSequence

    def getReadInstructionCount(self):
        readInstructionCount = 0
        for instruction in self.instructionSequence:
            if instruction.isReadInstruction():
                readInstructionCount += 1
        return readInstructionCount

    def getWriteInstructionCount(self):
        writeInstructionCount = 0
        for instruction in self.instructionSequence:
            if instruction.isWriteInstruction():
                writeInstructionCount += 1
        return writeInstructionCount

    def getLogicInstructionCount(self):
        logicInstructionCount = 0
        for instruction in self.instructionSequence:
            if not (instruction.isReadInstruction() or instruction.isWriteInstruction()):
                logicInstructionCount += 1
        return logicInstructionCount

    def generateStats(self):
        return f"#R/#W/#L: {self.getReadInstructionCount()}, {self.getWriteInstructionCount()}, {self.getLogicInstructionCount()}"

