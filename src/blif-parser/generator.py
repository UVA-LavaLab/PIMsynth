from parser import *


class Generator():
    def __init__(self, parser):
        self.parser = parser
        self.dataType = "uint64_t"

    def generateCode(self):
        str = ""
        str += self.generateHeaderFile() + "\n\n"
        str += self.generateHeader()
        str += self.generateBody()
        return str

    def generateHeaderFile(self):
        return "#include <cstdint>"

    def generateHeader(self):
        str = "void "
        str += self.generateFunctionName()
        str += "(\n"
        str += self.generateInputArgs()
        str += self.generateOutputArgs()
        str += ")\n"
        return str

    def generateFunctionName(self):
        str = self.parser.moduleName
        return str

    def generateInputArgs(self):
        str = ""
        for item in self.parser.inputsList:
            str += "\t" + self.dataType + " " + item + ",\n"
        return str

    def generateOutputArgs(self):
        str = ""
        numOutputs = len(self.parser.outputsList)
        i = 0
        for item in self.parser.outputsList:
            str += "\t" + self.dataType + " &" + item
            if (i != numOutputs - 1):
                str += ",\n"
            else:
                str += "\n"
            i += 1
        return str

    def generateBody(self):
        str = "{\n"
        str += self.generateTemporaryVariables()
        str += self.generateStamentSequence()
        str += "\n}\n"
        return str

    def generateTemporaryVariables(self):
        str = "\t" + self.dataType + " "
        numOutputs = len(self.parser.wireList)
        i = 0
        for item in self.parser.wireList:
            str += item
            if (i != numOutputs - 1):
                str += ", "
            else:
                str += ";\n"
            i += 1
        return str

    def generateStamentSequence(self):
        str = ""
        for item in self.parser.statementList:
            str += "\t" + item.output + " = "
            if item.name.startswith('inv1'):
                str += "~" + item.inputList[0] + ";\n"
            elif item.name.startswith('and2'):
                str += "(" + item.inputList[0] + " & " + item.inputList[1] + ");\n"
            elif item.name.startswith('or2'):
                str += "(" + item.inputList[0] + " | " + item.inputList[1] + ");\n"
            elif item.name.startswith('nand2'):
                str += "~(" + item.inputList[0] + " & " + item.inputList[1] + ");\n"
            elif item.name.startswith('nor2'):
                str += "~(" + item.inputList[0] + " | " + item.inputList[1] + ");\n"
            elif item.name.startswith('xor2'):
                str += "(" + item.inputList[0] + " ^ " + item.inputList[1] + ");\n"
            elif item.name.startswith('xnor2'):
                str += "~(" + item.inputList[0] + " ^ " + item.inputList[1] + ");\n"
            else:
                print('Error: Unhandled item name', item.name)

        return str
