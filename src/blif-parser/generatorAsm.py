from parser import *


class GeneratorAsm():
    def __init__(self, parser, num_regs):
        self.parser = parser
        #self.dataType = "uint64_t"
        self.dataType = "int"
        self.num_regs = num_regs

    def generateCode(self):
        str = ""
        str += self.generateHeaderFile() + "\n\n"
        str += self.generateHeader()
        str += self.generateBody()
        return str

    def generateHeaderFile(self):
        #return "#include <cstdint>"
        return ""

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
            str += "\t" + self.dataType + " *" + item + "_p,\n"
        return str

    def generateOutputArgs(self):
        str = ""
        numOutputs = len(self.parser.outputsList)
        i = 0
        for item in self.parser.outputsList:
            #str += "\t" + self.dataType + " &" + item
            str += "\t" + self.dataType + " *" + item + "_p"
            if (i != numOutputs - 1):
                str += ",\n"
            else:
                str += "\n"
            i += 1
        return str

    def generateBody(self):
        str = "{\n"
        str += self.generateTemporaryVariables()
        str += self.generateTemporaryVariablesIn();
        str += self.generateTemporaryVariablesOut();
        str += "\n"
        str += self.generateStamentSequenceAsm()
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

    def generateTemporaryVariablesIn(self):
        str = "\t" + self.dataType + " "
        numInputs = len(self.parser.inputsList)
        i = 0
        for item in self.parser.inputsList:
            str += item + " = *" + item + "_p"
            if (i != numInputs - 1):
                str += ", "
            else:
                str += ";\n"
            i += 1
        return str

    def generateTemporaryVariablesOut(self):
        str = "\t" + self.dataType + " "
        numOutputs = len(self.parser.outputsList)
        i = 0
        for item in self.parser.outputsList:
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
            if "inv1" in item.name:
                str += "~" + item.inputList[0] + ";\n"
            if "nand2" in item.name:
                str += "~(" + item.inputList[0] + " & " + item.inputList[1] + ");\n"
            if "nor2" in item.name:
                str += "~(" + item.inputList[0] + " | " + item.inputList[1] + ");\n"

        return str

    def generateStamentSequenceAsm(self):
        code = ''
        # reserve risc-v registers
        regs = ['"ra"']
        for i in range(8):
            regs.append('"a' + str(i) + '"')
        for i in range(12):
            regs.append('"s' + str(i) + '"')
        for i in range(self.num_regs, 7):
            regs.append('"t' + str(i) + '"')
        clobber = ','.join(regs)

        # generate inline asm
        code += '\tasm("########## BEGIN ##########");\n'
        for item in self.parser.statementList:
            if item.name.startswith("inv1"):
                code += '\tasm("not %%0, %%1" : "=r" (%s) : "r" (%s) : %s );\n' % (item.output, item.inputList[0], clobber)
            elif item.name.startswith("and2"):
                code += '\tasm("and %%0, %%1, %%2" : "=r" (%s) : "r" (%s), "r" (%s) : %s );\n' % (item.output, item.inputList[0], item.inputList[1], clobber)
            elif item.name.startswith("nand2"):
                code += '\tasm("and %%0, %%1, %%2\\nnot %%0, %%0" : "=r" (%s) : "r" (%s), "r" (%s) : %s );\n' % (item.output, item.inputList[0], item.inputList[1], clobber)
            elif item.name.startswith("or2"):
                code += '\tasm("or %%0, %%1, %%2" : "=r" (%s) : "r" (%s), "r" (%s) : %s );\n' % (item.output, item.inputList[0], item.inputList[1], clobber)
            elif item.name.startswith("nor2"):
                code += '\tasm("or %%0, %%1, %%2\\nnot %%0, %%0" : "=r" (%s) : "r" (%s), "r" (%s) : %s );\n' % (item.output, item.inputList[0], item.inputList[1], clobber)
            elif item.name.startswith("xor2"):
                code += '\tasm("xor %%0, %%1, %%2" : "=r" (%s) : "r" (%s), "r" (%s) : %s );\n' % (item.output, item.inputList[0], item.inputList[1], clobber)
            elif item.name.startswith("xnor2"):
                code += '\tasm("xor %%0, %%1, %%2\\nnot %%0, %%0" : "=r" (%s) : "r" (%s), "r" (%s) : %s );\n' % (item.output, item.inputList[0], item.inputList[1], clobber)
            else:
                print('Error: Unhandled item name', item.name)
        code += '\tasm("########## END ##########");\n'

        # assign results
        code += "\n"
        for item in self.parser.outputsList:
            code += "\t*" + item + '_p = ' + item + ";\n"

        return code

