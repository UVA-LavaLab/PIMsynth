

class PimEvalAPICodeGenerator:
    def __init__(self, instructionSequence, tempManager, functionName, ports):
        self.instructionSequence = instructionSequence
        self.tempTable = tempManager
        self.functionName = functionName
        self.ports = ports

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
        for port in sorted(list(self.ports)):
            code += "PimObjId " + port + ",\n"
        return code

    def generateFunctionBody(self):
        code = "{\n"
        code += self.generateTemporaryVariables()
        code += "\n"
        code += self.generateStatementsAsm()
        code += "}\n"
        return code

    def generateTemporaryVariables(self):
        code = ""
        # TODO
        return code

    def generateStatementsAsm(self):
        code = ""
        return code

