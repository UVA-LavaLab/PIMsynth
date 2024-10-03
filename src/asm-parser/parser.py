
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
        return f"PortInfo(Value: {self.val}, Line: {self.line})"

class Instruction(Statement):
    def __init__(self, opCode, operandsList, line):
        super().__init__(line)
        self.opCode = opCode
        self.operandsList = operandsList

    def __str__(self):
        operandsListStr = ', '.join(self.operandsList)
        return f"Instruction(Opcode: {self.opCode}, Operands List: [{operandsListStr}], Line: {self.line})"

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

class PortInfo(Statement):
    def __init__(self, varName, line):
        super().__init__(line)
        self.varName = varName

    def __str__(self):
        return f"PortInfo(VarName: {self.varName}, Line: {self.line})"

    def isInputPort(self):
        pattern = r"pi[0-9]+"
        return bool(re.search(pattern, self.varName))

    def isOutputPort(self):
        pattern = r"po[0-9]+"
        return bool(re.search(pattern, self.varName))

    def isPointer(self):
        return "_p" in self.varName

    def isTempVariable(self):
        return "new_" in self.varName

    def getPortName(self):
        parts = self.varName.split(":")
        if len(parts) == 2:
            return parts[1]
        else:
            return None

class Parser():
    def __init__(self, moduleName):
        self.moduleName = moduleName
        self.statementList = []

    def parse(self, inLines):
        # Regular expression to capture the port name only
        port_regex = re.compile(r"#DEBUG_VALUE:\s*([a-zA-Z0-9_]+:[a-zA-Z0-9_]+)")

        # Regular expression to match assembly instructions
        instruction_regex = re.compile(r"^\s*([a-zA-Z]+)\s+([a-zA-Z0-9]+)\s*,?\s*([a-zA-Z0-9()]+)?\s*(?:,\s*([a-zA-Z0-9()]+))?\s*(?:,\s*([a-zA-Z0-9()]+))?", re.MULTILINE)

        lineNumber = 1
        for line in inLines:
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

