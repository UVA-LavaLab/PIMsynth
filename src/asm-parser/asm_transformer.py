
from parser import *

class SymbolTable:
    def __init__(self):
        self.dictionary = {}

    def getSymbol(self, key):
        # Return the value for the given key, or None if key doesn't exist
        return self.dictionary.get(key, None)

    def addSymbol(self, key, val):
        # Add the key-value pair to the dictionary
        self.dictionary[key] = val

    def printSymbols(self):
        if not self.dictionary:
            print("Symbol table is empty.")
        else:
            for key, val in self.dictionary.items():
                print(f"{key}: {val}")

    def removeSymbol(self, key):
        # Remove the key from the dictionary if it exists, else raise KeyError
        if key in self.dictionary:
            del self.dictionary[key]
        else:
            raise KeyError(f"Symbol '{key}' not found.")

class TempManager:
    def __init__(self):
        self.isAllocated = []  # Example: [True, True, False, True]

    def newTemp(self):
        # Find the first False and set it to True, then return the index
        for i, allocated in enumerate(self.isAllocated):
            if not allocated:
                self.isAllocated[i] = True
                return i
        # If no False is found, append a new True and return its index
        self.isAllocated.append(True)
        return len(self.isAllocated) - 1

    def freeTemp(self, tempStr):
        index = int(tempStr[4:])
        # Set the element at the specified index to False
        if 0 <= index < len(self.isAllocated):
            self.isAllocated[index] = False
        else:
            raise IndexError("Index out of bounds")

class AsmTransformer:
    def __init__(self, riscvStatementList):
        self.riscvStatementList = riscvStatementList
        self.bitSerialStatementList = []
        self.symbolTable = SymbolTable()
        self.tempManager = TempManager()
        self.transform()

    def transform(self):
        statementIndex = 0
        while (statementIndex < len(self.riscvStatementList)):
            statement = self.riscvStatementList[statementIndex]
            if type(statement) == Instruction:
                if statement.isLoadInstruction():
                    self.transformLoadInstruction(statementIndex)
                elif statement.isStoreInstruction():
                    self.transformStoreInstruction(statementIndex)
            if type(statement) == Directive:
                if statement.val == "#APP":
                    self.transformInlineAssembly(statementIndex)
            statementIndex += 1

    def transformLoadInstruction(self, statementIndex):
        riscvInstruction = self.riscvStatementList[statementIndex]
        portInfo = self.riscvStatementList[statementIndex + 1]
        line = riscvInstruction.line
        # Input Load
        if type(portInfo) == PortInfo and portInfo.isInputPort():
            sourceOperand = portInfo.getPortName() # Subsitute the source operand with the input port name
            destinationOperand = riscvInstruction.operandsList[0]
            operandsList = [destinationOperand, sourceOperand]

            # Add destinationOperand:sourceOperand to the symbol table
            self.symbolTable.addSymbol(sourceOperand, destinationOperand)

        elif type(portInfo) == PortInfo and portInfo.isPointer():
            print(f"Info: lw instruction at line {line} was ignored.") # Ignore the instruction
            return

        else:
            if type(portInfo) == PortInfo and portInfo.isOutputPort():
                print(f"Info: lw instruction at line {line} was ignored.") # Ignore the instruction
                return

            # Temp variable Re-load
            else:
                # Replace the source operand from the temp from the symbol table
                oldSourceOperand = riscvInstruction.operandsList[1]
                sourceOperand = self.symbolTable.getSymbol(oldSourceOperand)
                if sourceOperand == None:
                    return

                print(f"Info: temp varialbe re-load at line {line}.")
                # Free the temp varialbe
                # self.tempManager.freeTemp(sourceOperand)
                # TODO: The re-load may happen later! The temp can not be freed always. Check the cases when can be freed.

                destinationOperand = riscvInstruction.operandsList[0]
                operandsList = [destinationOperand, sourceOperand]

        bitSerialOpcode = "read"
        bitSerialInstruction = Instruction(bitSerialOpcode, operandsList, line)
        self.bitSerialStatementList.append(bitSerialInstruction)

    def transformStoreInstruction(self, statementIndex):
        riscvInstruction = self.riscvStatementList[statementIndex]
        portInfo = self.riscvStatementList[statementIndex + 1]
        line = riscvInstruction.line
        bitSerialOpcode = "write"
        # Spill Temp
        if type(portInfo) == PortInfo and portInfo.isTempVariable():
            # Allocate new temp
            newTempIndex = self.tempManager.newTemp()
            newTempStr = "temp" + str(newTempIndex)

            print(f"Info: sw instruction is spilling the temp {newTempStr} at line {line}.")

            # Add temp to the symbol table
            oldDestinationOperand = riscvInstruction.operandsList[1]
            self.symbolTable.addSymbol(oldDestinationOperand, newTempStr)

            # Replace the destination operand with the temp variable
            destinationOperand = newTempStr

            sourceOperand = riscvInstruction.operandsList[0]
            operandsList = [sourceOperand, destinationOperand]

        else:
            # Check if the source temp has a row in the symbol table
            sourceOperand = riscvInstruction.operandsList[0]
            symbolTableVal = self.symbolTable.getSymbol(sourceOperand)
            if symbolTableVal != None:
                # Spill Input
                self.tempManager.freeTemp(sourceOperand)

                # Remove the row in the symbol table
                self.symbolTable.removeSymbol(sourceOperand)

            print(f"Info: sw instruction at line {line} was ignored.") # Ignore the instruction
            return

        bitSerialOpcode = "write"
        bitSerialInstruction = Instruction(bitSerialOpcode, operandsList, line)
        self.bitSerialStatementList.append(bitSerialInstruction)

    def getInlineInstructionSequence(self, statementIndex):
        i = statementIndex + 1
        instructionSequence = []
        while True:
            statement = self.riscvStatementList[i]
            if type(statement) == Directive:
                if statement.val == "#NO_APP":
                    break
            instructionSequence.append(statement)
            i += 1
        return instructionSequence

    def transformInlineAssembly(self, statementIndex):
        firstRiscvInstruction = self.riscvStatementList[statementIndex + 1]
        line = firstRiscvInstruction.line

        # Get inline assembly instruction list
        instructionSequence = self.getInlineInstructionSequence(statementIndex)

        # Map riscv sequence instruction to bit-serial instruction
        newOpCode = self.getOpCode(instructionSequence)
        if newOpCode == None:
            return
        print(f"Info: Mapped opcode for the line {line} is {newOpCode}.")

        # Get the input operands list
        sourceOperandList = firstRiscvInstruction.operandsList[1:]
        lastRiscvInstruction = instructionSequence[len(instructionSequence) - 1]
        destinationOperand = lastRiscvInstruction.operandsList[0]
        operandsList = [destinationOperand] + sourceOperandList
        bitSerialInstruction = Instruction(newOpCode, operandsList, line)
        self.bitSerialStatementList.append(bitSerialInstruction)


        # Check if the destination operand is the output port
        portInfoIndex = statementIndex + len(instructionSequence) + 2
        portInfo = self.riscvStatementList[portInfoIndex]
        if type(portInfo) == PortInfo and portInfo.isOutputPort():
            # Add a write instruction from the destination operand to the output port
            writeOpCode = "write"
            writeSourceOperand = destinationOperand
            writeDestinationOperand = portInfo.getPortName()
            writeOperandsList = [writeSourceOperand, writeDestinationOperand]
            writeInstruction = Instruction(writeOpCode, writeOperandsList, line)
            self.bitSerialStatementList.append(writeInstruction)


    def getOpCode(self, instructionSequence):
        transformationRules = {
            ('xor', 'not'): 'xnor',
            ('and', 'not'): 'not',
        }
        mappedOpcodes = []  # To store the mapped opcodes
        i = 0
        while i < len(instructionSequence):
            matched = False
            currentOp = instructionSequence[i].opCode

            # Try to match a sequence starting at the current position
            for sequence, targetOpcode in transformationRules.items():
                seqLen = len(sequence)

                # Check if we have enough instructions remaining and the sequence matches
                if i + seqLen <= len(instructionSequence) and all(
                    instructionSequence[i + j].opCode == sequence[j] for j in range(seqLen)
                ):
                    mappedOpcodes.append(targetOpcode)
                    i += seqLen  # Skip the instructions that are part of the matched sequence
                    matched = True
                    break

            # If no transformation matched, just add the current opcode
            if not matched:
                mappedOpcodes.append(currentOp)
                i += 1

        if len(mappedOpcodes) == 1:
            return mappedOpcodes[0]
        else:
            return None

    def getBitSerialAsm(self):
        return self.bitSerialStatementList


