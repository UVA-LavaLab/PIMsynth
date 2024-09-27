import re
import math

# Util function
def findTempVarIndex(inputString):
    pattern = r'temp\d+'
    match = re.search(pattern, inputString)
    if match:
        return match.start()
    else:
        return -1

def concatenateListElements(lst):
    return ', '.join(map(str, lst))

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
        self.functionName = functionName
        self.ports = sorted(list(ports))
        self.tempVarMapList = self.getTempVarMapList()

    def generateCode(self):
        code = ""
        # code += self.generateHeaderFiles()
        code += self.generateFunctionSignature()
        code += self.generateFunctionBody()
        return code

    def generateFunctionSignature(self):
        code = "void "
        code += self.functionName
        code += "(\n"
        code += self.generateFunctionArgs()
        code += ")\n"
        return code

    def generateFunctionArgs(self):
        code = ""
        for port in self.ports:
            code += "\t" + "PimObjId " + port + ",\n"
        return code

    def generateFunctionBody(self):
        code = "{\n"
        code += self.generateTemporaryVariables()
        code += "\n\n"
        code += self.generateStatementsAsm()
        code += "}\n"
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
        numberOfTempVar = math.ceil(numberOfTempVars / dataTypeBitWidth)
        firstIoPort = self.ports[0]

        # Helper function to generate a single temp variable allocation code
        def allocateTempVariable(index):
            return f"\tPimObjId tempObj{index} = pimAllocAssociated({dataTypeBitWidth}, {firstIoPort}, PIM_INT{dataTypeBitWidth});"

        # Generate code for each temp variable
        code = "\n".join(allocateTempVariable(i) for i in range(numberOfTempVar))

        return code

    def mapPimAsmRegToPimEvalAPI(self, pimAsmReg):
        regMap = {
            "t0": "PIM_RREG_R1",
            "t1": "PIM_RREG_R2",
            "t2": "PIM_RREG_R3",
            "t3": "PIM_RREG_R4",
            "t4": "PIM_RREG_R5"
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
            return f"tempObj{tempObjIndex}, {offset}"
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
        code += f"\tpimOpWriteSaToRow({destinationOperand});\n\n"

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
                pass
        return code

