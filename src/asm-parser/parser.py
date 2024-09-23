
import re

class Statement:
    def __init__(self, line):
        self.line = line

class Instruction(Statement):
    def __init__(self, opCode, operandsList, line):
        super().__init__(line)
        self.opCode = opCode
        self.operandsList = operandsList

    def __str__(self):
        operandsListStr = ', '.join(self.operandsList)
        return f"Instruction(Opcode: {self.opCode}, Operands List: [{operandsListStr}], Line: {self.line})"

class PortInfo(Statement):
    def __init__(self, varName, line):
        super().__init__(line)
        self.varName = varName

    def __str__(self):
        return f"PortInfo(VarName: {self.varName}, Line: {self.line})"

class Parser():
    def __init__(self, moduleName):
        self.moduleName = moduleName
        self.statementList = []

    def parse(self, inLines):
        # Regular expression to capture the port name only
        port_regex = re.compile(r"#DEBUG_VALUE:\s*([a-zA-Z0-9_]+:[a-zA-Z0-9_]+)")

        # Regular expression to match assembly instructions
        instruction_regex = re.compile(r"^\s*([a-zA-Z]+)\s+([a-zA-Z0-9]+)\s*,?\s*([a-zA-Z0-9()]+)?\s*(?:,\s*([a-zA-Z0-9()]+))?\s*(?:,\s*([a-zA-Z0-9()]+))?", re.MULTILINE)

        lineNumber = 0
        for line in inLines:
            # Find match
            match = port_regex.search(line)

            if match:
                portName = match.group(1)  # The port name (e.g., fullAdder1:pi0)
                portInfo = PortInfo(portName, lineNumber)
                self.statementList.append(portInfo)

            # Find all matches in the assembly code
            matches = instruction_regex.findall(line)

            # Process and display the results
            for match in matches:
                opCode = match[0]  # The instruction itself (e.g., 'and')
                operandsList = [operand for operand in match[1:] if operand]  # Filter out empty operands
                instruction = Instruction(opCode, operandsList, lineNumber)
                self.statementList.append(instruction)

            lineNumber += 1

    def printStatementList(self):
        for statement in self.statementList:
            print(statement)

