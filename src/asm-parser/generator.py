#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: generator.py
Description: bit-serial code generator in either assembly or PIMeval API
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu> - RISCV-to-BITSERIAL code generator framework
Date: 2024-09-27
"""

import re
import math

# Util function
def findTempVarIndex(inputString):
    if inputString.startswith("temp"):
        return int(inputString[4:])
    else:
        return -1

def concatenateListElements(lst):
    return ', '.join(map(str, lst))

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


class PimEvalAPICodeGenerator:
    def __init__(self, instructionSequence, functionName, ports):
        self.instructionSequence = instructionSequence
        self.numberOfTempVarObjs = -1
        self.functionName = functionName
        self.ports = sorted(list(ports))
        self.tempVarMapList = self.getTempVarMapList()

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

    def generateFunctionArgs(self):
        code = ""
        numberOfPorts = len(self.ports)
        i = 0
        for port in self.ports:
            isLastElement = (i == numberOfPorts - 1)
            code += "\t" + "PimObjId " + port
            if isLastElement:
                code += "\n"
            else:
                code += ",\n"
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
        firstIoPort = self.ports[0]

        # Helper function to generate a single temp variable allocation code
        def allocateTempVariable(index):
            return f"\tPimObjId tempObj{index} = pimAllocAssociated({firstIoPort}, PIM_INT{dataTypeBitWidth});"

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

    def mapPimAsmRegToPimEvalAPI(self, pimAsmReg):
        regMap = {
            "t0": "PIM_RREG_R1",
            "t1": "PIM_RREG_R2",
            "t2": "PIM_RREG_R3",
            "t3": "PIM_RREG_R4",
            "t4": "PIM_RREG_R5",
            "t5": "PIM_RREG_R6",
            "t6": "PIM_RREG_R7"
        }
        if pimAsmReg in regMap:
            return regMap[pimAsmReg]
        else:
            raise ValueError(f"Invalid register: {pimAsmReg}")

    def mapPimAsmOpCodeToPimEvalAPI(self, pimOpCode):
        opCodeMap = {
            "not": "pimOpNot",
            "and": "pimOpAnd",
            "or": "pimOpOr",
            "xor": "pimOpXor",
            "nand": "pimOpNand",
            "nor": "pimOpNor",
            "xnor": "pimOpXnor"
        }
        if pimOpCode in opCodeMap:
            return opCodeMap[pimOpCode]
        else:
            raise ValueError(f"Invalid PIM opcode: {pimOpCode}")

    def generateInstructionComment(self, instruction):
        return f"\t// {instruction.opCode} {concatenateListElements(instruction.operandsList)} (Line: {instruction.line})\n"

    def formatOperand(self, operand, isSource=True):
        if "temp" in operand:
            tmpVarIndex = findTempVarIndex(operand)
            tempObjIndex, offset = self.mapVarIndex(tmpVarIndex)
            return f"tempObj{tempObjIndex}, {offset}" if isSource else f"tempObj{tempObjIndex}"
        return f"{operand}, 0" if isSource else operand

    def generateReadInstruction(self, instruction):
        code = self.generateInstructionComment(instruction)

        sourceOperand = self.formatOperand(instruction.operandsList[1])
        code += f"\tpimOpReadRowToSa({sourceOperand});\n"

        destinationOperand = instruction.operandsList[0]
        firstIoPort = self.ports[0]
        code += f"\tpimOpMove({firstIoPort}, PIM_RREG_SA, {self.mapPimAsmRegToPimEvalAPI(destinationOperand)});\n\n"

        return code

    def generateWriteInstruction(self, instruction):
        code = self.generateInstructionComment(instruction)

        sourceOperand = instruction.operandsList[0]
        firstIoPort = self.ports[0]
        code += f"\tpimOpMove({firstIoPort}, {self.mapPimAsmRegToPimEvalAPI(sourceOperand)}, PIM_RREG_SA);\n"

        destinationOperand = self.formatOperand(instruction.operandsList[1], isSource=False)
        code += f"\tpimOpWriteSaToRow({destinationOperand}, 0);\n\n"

        return code

    def generateLogicalInstructionOperands(self, operandsList):
        reorderedOperandList = operandsList[1:] + [operandsList[0]]
        functionOperands = list(map(self.mapPimAsmRegToPimEvalAPI, reorderedOperandList))
        code = f"{concatenateListElements(functionOperands)}"
        return code

    def generateLogicInstruction(self, instruction):
        code = self.generateInstructionComment(instruction)

        pimEvalFunctionName = self.mapPimAsmOpCodeToPimEvalAPI(instruction.opCode)
        firstIoPort = self.ports[0]
        code += f"\t{pimEvalFunctionName}({firstIoPort}, {self.generateLogicalInstructionOperands(instruction.operandsList)});\n\n"
        return code

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

