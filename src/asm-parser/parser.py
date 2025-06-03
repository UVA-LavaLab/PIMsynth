
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: parser.py
Description: Parse RISCV assembly code.
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Date: 2024-09-27
"""

import re

class Statement:
    def __init__(self, line):
        self.line = line

class Directive(Statement):
    def __init__(self, val, line):
        super().__init__(line)
        self.val = val

    def __str__(self):
        return f"{self.val:<32} | Line {self.line:<5})"

class Instruction(Statement):
    def __init__(self, opCode, operandsList, line):
        super().__init__(line)
        self.opCode = opCode
        self.operandsList = operandsList

    def __str__(self):
        operandsListStr = ', '.join(self.operandsList)
        return f"{self.opCode:<10} {operandsListStr:<32} | Line {self.line})"

    def isLoadInstruction(self):
        if "lw" in self.opCode:
            return True
        else:
            return False

    def isStoreInstruction(self):
        if "sw" in self.opCode:
            return True
        else:
            return False

    def isMoveInstruction(self):
        if "mv" in self.opCode:
            return True
        else:
            return False

    def isReadInstruction(self):
        if "read" in self.opCode:
            return True
        else:
            return False

    def isWriteInstruction(self):
        if "write" in self.opCode:
            return True
        else:
            return False

    def getOpCode(self):
        return self.opCode

    def getOperandsList(self):
        return self.operandsList

class PortInfo(Statement):
    def __init__(self, varName, line):
        super().__init__(line)
        self.varName = varName

    def __str__(self):
        return f"PortInfo(VarName: {self.varName}, Line: {self.line})"

    def isInputPort(self, inputList):
        return (self.varName in inputList)

    def isOutputPort(self, outputList):
        return (self.varName in outputList)

    def isTempVariable(self):
        return "new_" in self.varName

    def getPortName(self):
        return self.varName

class Parser():
    def __init__(self, moduleName):
        self.moduleName = moduleName
        self.statementList = []
        self.inputList = []
        self.outputList = []

    def parse(self, inLines):
        # Regular expression to capture the port name only
        port_regex = re.compile(r"#DEBUG_VALUE:\s*[a-zA-Z0-9_]+:([a-zA-Z0-9_]+)")

        # Regular expression to match assembly instructions
        instruction_regex = re.compile(r"^\s*([a-zA-Z]+)\s+([a-zA-Z0-9]+)\s*,?\s*([a-zA-Z0-9()]+)?\s*(?:,\s*([a-zA-Z0-9()]+))?\s*(?:,\s*([a-zA-Z0-9()]+))?", re.MULTILINE)

        # IO variable info and name
        matchVarName_regex = r'#DEBUG_VALUE:\s*func:([a-zA-Z0-9_]+)\s*.*'

        lineNumber = 1
        for line in inLines:
            # Create the port name list

            matchVarName = re.match(matchVarName_regex, line)
            if matchVarName:
                varName = matchVarName.group(1)
                if varName.endswith("_pi"):
                    self.inputList.append(varName.replace("_pi", ""))
                elif varName.endswith("_po"):
                    self.outputList.append(varName.replace("_po", ""))

            # Find port information match
            match = port_regex.search(line)

            if match:
                portName = match.group(1)  # The port name (e.g., fullAdder1:pi0)
                portInfo = PortInfo(portName, lineNumber)
                self.statementList.append(portInfo)

            # Find all matches in the assembly code
            matches = instruction_regex.findall(line)

            # Process and display the results
            for match in matches:
                opCode = match[0]  # The opCode (e.g., 'and')
                operandsList = [operand for operand in match[1:] if operand]  # Filter out empty operands
                instruction = Instruction(opCode, operandsList, lineNumber)
                self.statementList.append(instruction)

            # Find directive
            if "APP" in line:
                directive = Directive(line.strip(), lineNumber)
                self.statementList.append(directive)

            lineNumber += 1

    def printStatementList(self):
        for statement in self.statementList:
            print(statement)


    def processStatementList(self):
        pass

