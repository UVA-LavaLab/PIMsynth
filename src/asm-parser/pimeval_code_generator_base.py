#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: pimeval_code_generator_base.py
Description: bit-serial code generator in PIMeval API base class
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu> - RISCV-to-BITSERIAL code generator framework
Date: 2025-05-17
"""

import re
import math
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util import *

# Util function
def findTempVarIndex(inputString):
    if inputString.startswith("temp"):
        return int(inputString[4:])
    else:
        return -1

class PimEvalAPICodeGeneratorBase:
    def __init__(self, instructionSequence, functionName, ports):
        self.instructionSequence = instructionSequence
        self.numberOfTempVarObjs = -1
        self.functionName = functionName
        self.ports = sorted(list(ports))
        self.tempVarMapList = self.getTempVarMapList()
        self.firstIoPort = self.countBits(self.ports)[0][0]

    def generateCode(self):
        code = f"#ifndef {self.functionName.upper()}_H\n"
        code += f"#define {self.functionName.upper()}_H\n"
        code += self.generateHeaderFiles()
        code += self.generateFunctionSignature()
        code += self.generateFunctionBody()
        code += "#endif\n\n"
        return code

    def generateHeaderFiles(self):
        return "#include \"libpimeval.h\"\n"

    def generateFunctionSignature(self):
        code = "void "
        code += self.functionName
        code += "(\n"
        code += self.generateFunctionArgs()
        code += ")\n"
        return code

    def countBits(self, portList):
        bitCounts = {}
        for item in portList:
            # Check if the port name contains an index
            parts = item.split('_')
            if len(parts) >= 3 and parts[1].isdigit():
                # Port name with an index
                variableName = parts[0]
            else:
                # Port name without an index
                variableName = item

            # Increment the count for this variable
            bitCounts[variableName] = bitCounts.get(variableName, 0) + 1

        # Convert the dictionary to a list of tuples
        return [(variable, count) for variable, count in bitCounts.items()]

    def generateFunctionArgs(self):
        code = ""
        numberOfPorts = len(self.ports)
        i = 0
        pimObjs = self.countBits(self.ports)
        numberOfObjs = len(pimObjs)
        i = 0
        for pimObj in pimObjs:
            isLastElement = (i == numberOfObjs - 1)
            code += "\t" + "PimObjId " + pimObj[0]
            if not isLastElement:
                code += ", "
            code += f" /* {pimObj[1]} bits */ \n"
            i += 1
        return code

    def generateFunctionBody(self):
        code = "{\n"
        code += self.generateTemporaryVariables()
        code += "\n\n"
        code += self.generateStatementsAsm()
        code += "\n"
        code += self.generateTemporaryVariablesFreeFunctions()
        code += "\n}\n"
        return code

    def getTempVarList(self):
        tempVarSet = set()
        for instruction in self.instructionSequence:
            for operand in instruction.operandsList:
                if "temp" in operand:
                    tempVarSet.add(operand)
        return list(tempVarSet)

    def getDataTypeBitWidth(self):
        dataTypeBitWidthList = [8, 16, 32, 64]
        selectedDataTypeWidth = dataTypeBitWidthList[-1]
        numberOfTempVars = len(self.getTempVarList())
        for dataTypeBitWidth in dataTypeBitWidthList:
            if numberOfTempVars <= dataTypeBitWidth:
                selectedDataTypeWidth = dataTypeBitWidth
        return selectedDataTypeWidth

    def mapVarIndex(self, tmpVarIndex):
        dataTypeBitWidth = self.getDataTypeBitWidth()
        return (tmpVarIndex // dataTypeBitWidth, tmpVarIndex % dataTypeBitWidth)

    def getTempVarMapList(self):
        tempVarMapList = list()
        for tempVar in self.getTempVarList():
            tmpVarIndex = findTempVarIndex(tempVar)
            pimObjIndex = self.mapVarIndex(tmpVarIndex)

    def generateTemporaryVariables(self):
        dataTypeBitWidth = self.getDataTypeBitWidth()
        numberOfTempVars = len(self.getTempVarList())
        self.numberOfTempVarObjs = math.ceil(numberOfTempVars / dataTypeBitWidth)

        # Helper function to generate a single temp variable allocation code
        def allocateTempVariable(index):
            return f"\tPimObjId tempObj{index} = pimAllocAssociated({self.firstIoPort}, PIM_INT{dataTypeBitWidth});"

        # Generate code for each temp variable
        code = "\n".join(allocateTempVariable(i) for i in range(self.numberOfTempVarObjs))
        return code

    def generateTemporaryVariablesFreeFunctions(self):
        # Helper function to generate a single temp variable free code
        def freeTempVariable(index):
            return f"\tpimFree(tempObj{index});"

        # Generate code for each temp variable
        code = "\n".join(freeTempVariable(i) for i in range(self.numberOfTempVarObjs))
        return code

    def generateReadInstruction(self, instruction):
        raise NotImplementedError("Error: Subclasses must implement this method.")

    def generateWriteInstruction(self, instruction):
        raise NotImplementedError("Error: Subclasses must implement this method.")

    def generateLogicInstruction(self, instruction):
        raise NotImplementedError("Error: Subclasses must implement this method.")

    def generateStatementsAsm(self):
        code = ""
        for instruction in self.instructionSequence:
            if instruction.opCode == "read":
                code += self.generateReadInstruction(instruction)
            elif instruction.opCode == "write":
                code += self.generateWriteInstruction(instruction)
            else:
                code += self.generateLogicInstruction(instruction)
        return code

