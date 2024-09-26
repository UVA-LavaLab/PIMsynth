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
        code += "\n"
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
        code = ""
        dataTypeBitWidth = self.getDataTypeBitWidth()
        numberOfTempVars = len(self.getTempVarList())
        numberOfTempVar = math.ceil(numberOfTempVars / dataTypeBitWidth)
        firstIoPort = self.ports[0]
        for i in range(numberOfTempVar):
            code += "\t" + "PimObjId tmpObj" + str(i) + " = "
            code += "pimAllocAssociated(" + str(dataTypeBitWidth) + ", " + firstIoPort + ", PIM_INT" + str(dataTypeBitWidth) + ");"
        return code

    def generateStatementsAsm(self):
        code = ""
        return code

