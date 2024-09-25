
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
        self.ports = set()
        self.transform()

    def transform(self):
        for statementIndex, statement in enumerate(self.riscvStatementList):
            if isinstance(statement, Instruction):
                if statement.isLoadInstruction():
                    self.transformLoadInstruction(statementIndex)
                    continue
                if statement.isStoreInstruction():
                    self.transformStoreInstruction(statementIndex)
                    continue
            elif isinstance(statement, Directive) and statement.val == "#APP":
                self.transformInlineAssembly(statementIndex)

    def appendBitSerialInstruction(self, opcode, operands, line):
        bitSerialInstruction = Instruction(opcode, operands, line)
        self.bitSerialStatementList.append(bitSerialInstruction)

    def isInputPort(self, portInfo):
        """Check if the PortInfo is an input port."""
        if isinstance(portInfo, PortInfo) and portInfo.isInputPort():
            self.ports.add(portInfo.getPortName())
            return True
        return False

    def isPointer(self, portInfo):
        """Ignore lw instruction if the port is a pointer."""
        if isinstance(portInfo, PortInfo) and portInfo.isPointer():
            return True
        return False

    def isOutputPort(self, portInfo):
        """Check if the PortInfo is an output port."""
        if isinstance(portInfo, PortInfo) and portInfo.isOutputPort():
            self.ports.add(portInfo.getPortName())
            return True
        return False

    def handleInputPort(self, riscvInstruction, portInfo):
        """Handle load instruction for input port."""
        sourceOperand = portInfo.getPortName()  # Substitute the source operand with the input port name
        destinationOperand = riscvInstruction.operandsList[0]

        # Add destinationOperand:sourceOperand to the symbol table
        self.symbolTable.addSymbol(sourceOperand, destinationOperand)

        # Append the bit-serial instruction
        self.appendBitSerialInstruction("read", [destinationOperand, sourceOperand], riscvInstruction.line)

    def handleTempVariableReload(self, riscvInstruction):
        """Handle temp variable re-load if it's already in the symbol table."""
        oldSourceOperand = riscvInstruction.operandsList[1]
        sourceOperand = self.symbolTable.getSymbol(oldSourceOperand)

        if sourceOperand is None:
            return

        print(f"Info: temp variable re-load at line {riscvInstruction.line}.")
        destinationOperand = riscvInstruction.operandsList[0]

        # Append the bit-serial instruction
        self.appendBitSerialInstruction("read", [destinationOperand, sourceOperand], riscvInstruction.line)

    def transformLoadInstruction(self, statementIndex):
        riscvInstruction = self.riscvStatementList[statementIndex]
        portInfo = self.riscvStatementList[statementIndex + 1]

        # Handle Input Port
        if self.isInputPort(portInfo):
            self.handleInputPort(riscvInstruction, portInfo)
            return

        # Ignore Pointer and Output Port
        if self.isPointer(portInfo) or self.isOutputPort(portInfo):
            print(f"Info: lw instruction at line {riscvInstruction.line} was ignored.")
            return

        # Handle Temp Variable Re-load
        self.handleTempVariableReload(riscvInstruction)

    def isTempVariable(self, portInfo):
        """Check if the PortInfo refers to a temp variable."""
        return isinstance(portInfo, PortInfo) and portInfo.isTempVariable()

    def handleTempVariableSpill(self, riscvInstruction, portInfo):
        """Handle store instruction for spilling temp variables."""
        line = riscvInstruction.line
        newTempIndex = self.tempManager.newTemp()
        newTempStr = f"temp{newTempIndex}"

        print(f"Info: sw instruction is spilling the temp {newTempStr} at line {line}.")

        # Add the new temp to the symbol table
        oldDestinationOperand = riscvInstruction.operandsList[1]
        self.symbolTable.addSymbol(oldDestinationOperand, newTempStr)

        # Replace the destination operand with the temp variable
        destinationOperand = newTempStr
        sourceOperand = riscvInstruction.operandsList[0]

        # Append the bit-serial instruction
        self.appendBitSerialInstruction("write", [sourceOperand, destinationOperand], line)

    def shouldIgnoreStoreInstruction(self, riscvInstruction, portInfo):
        """Ignore store instruction if source operand has no corresponding symbol."""
        line = riscvInstruction.line
        sourceOperand = riscvInstruction.operandsList[0]
        symbolTableVal = self.symbolTable.getSymbol(sourceOperand)

        if symbolTableVal is not None:
            # Spill input and clean up symbol table
            self.tempManager.freeTemp(sourceOperand)
            self.symbolTable.removeSymbol(sourceOperand)
            return False

        print(f"Info: sw instruction at line {line} was ignored.")
        return True

    def transformStoreInstruction(self, statementIndex):
        riscvInstruction = self.riscvStatementList[statementIndex]
        portInfo = self.riscvStatementList[statementIndex + 1]

        # Handle Temp Variable Spill
        if self.isTempVariable(portInfo):
            self.handleTempVariableSpill(riscvInstruction, portInfo)
            return

        # Ignore instruction if no temp variable is involved
        if self.shouldIgnoreStoreInstruction(riscvInstruction, portInfo):
            return

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

    def getMappedOpCode(self, instructionSequence, line):
        """Get the opcode mapped to the inline assembly instruction sequence."""
        newOpCode = self.getOpCode(instructionSequence)
        if newOpCode is None:
            print(f"Info: No mapped opcode found for inline assembly at line {line}.")
        else:
            print(f"Info: Mapped opcode for the line {line} is {newOpCode}.")
        return newOpCode

    def handleBitSerialInstruction(self, instructionSequence, newOpCode, firstRiscvInstruction):
        """Handle the transformation of the bit-serial instruction from inline assembly."""
        sourceOperandList = firstRiscvInstruction.operandsList[1:]
        lastRiscvInstruction = instructionSequence[-1]
        destinationOperand = lastRiscvInstruction.operandsList[0]

        operandsList = [destinationOperand] + sourceOperandList
        line = firstRiscvInstruction.line
        bitSerialInstruction = Instruction(newOpCode, operandsList, line)

        # Append the mapped bit-serial instruction
        self.bitSerialStatementList.append(bitSerialInstruction)

    def handleWriteToOutputPort(self, statementIndex, instructionSequence, line):
        """Handle writing to an output port after inline assembly."""
        portInfoIndex = statementIndex + len(instructionSequence) + 2
        portInfo = self.riscvStatementList[portInfoIndex]

        if self.isOutputPort(portInfo):
            destinationOperand = instructionSequence[-1].operandsList[0]
            writeSourceOperand = destinationOperand
            writeDestinationOperand = portInfo.getPortName()

            writeOpCode = "write"
            writeOperandsList = [writeSourceOperand, writeDestinationOperand]
            writeInstruction = Instruction(writeOpCode, writeOperandsList, line)

            # Append the write instruction for the output port
            self.bitSerialStatementList.append(writeInstruction)

    def transformInlineAssembly(self, statementIndex):
        instructionSequence = self.getInlineInstructionSequence(statementIndex)
        firstRiscvInstruction = self.riscvStatementList[statementIndex + 1]
        newOpCode = self.getMappedOpCode(instructionSequence, firstRiscvInstruction.line)

        if newOpCode is None:
            return

        # Handle the mapped bit-serial instruction
        self.handleBitSerialInstruction(instructionSequence, newOpCode, firstRiscvInstruction)

        # Handle write to output port if necessary
        self.handleWriteToOutputPort(statementIndex, instructionSequence, firstRiscvInstruction.line)

    def matchesSequence(self, instructionSequence, sequence):
        """Check if a given sequence of opcodes matches the transformation rule."""
        if len(instructionSequence) < len(sequence):
            return False

        return all(
            instructionSequence[i].opCode == sequence[i]
            for i in range(len(sequence))
        )

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

