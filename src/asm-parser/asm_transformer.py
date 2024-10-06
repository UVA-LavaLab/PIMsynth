#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: asm_transformer.py
Description: Translates RISCV assembly code to bit-serial assembly code
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Date: 2024-09-27
"""

from parser import *

class LinkedInstruction(Instruction):
    def __init__(self, opCode, operandsList, line, sourceInstructionList = None, suspended = False):
        super().__init__(opCode, operandsList, line)
        self.sourceInstructionList = sourceInstructionList
        self.suspended = suspended

    def __str__(self):
        operandsListStr = ', '.join(self.operandsList)
        if self.sourceInstructionList == None:
            sourceInstructionLinesStr = "X"
        else:
            sourceInstructionLines = [(str(instrunction.line) if instrunction != None else "-") for instrunction in self.sourceInstructionList]
            sourceInstructionLinesStr = ', '.join(sourceInstructionLines)
        return f"LinkedInstruction(Opcode: {self.opCode}, Operands List: [{operandsListStr}], Source Instrunctions Line: {sourceInstructionLinesStr}, Line: {self.line}, suspended: {self.suspended})"

    def unsuspend(self):
        self.suspended = False

    def getOpCode(self):
        return self.opCode

    def getOperandsList(self):
        return self.operandsList

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
                if isinstance(val, LinkedInstruction):
                    print(f"{key}: L{val.line}")
                else:
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

    def getDestinationOperandFromInstruction(self, instruction):
        if instruction.opCode == "write":
            return instruction.operandsList[1]
        else:
            return instruction.operandsList[0]

    def getDestinationOperand(self, opCode, operandsList):
        if opCode == "write":
            return operandsList[1]
        else:
            return operandsList[0]

    def appendBitSerialInstruction(self, opCode, operands, line, suspended=False):
        if opCode == "write":
            sourceInstructionList = [self.symbolTable.getSymbol(sourceOperand) for sourceOperand in [operands[0]]]
        elif opCode == "read":
            sourceInstructionList = [self.symbolTable.getSymbol(sourceOperand) for sourceOperand in operands[1:]]
        else:
            sourceInstructionList = [self.symbolTable.getSymbol(sourceOperand) for sourceOperand in operands[1:]]
        bitSerialInstruction = LinkedInstruction(opCode, operands, line, sourceInstructionList=sourceInstructionList, suspended=suspended)
        self.bitSerialStatementList.append(bitSerialInstruction)
        self.symbolTable.addSymbol(self.getDestinationOperand(opCode, operands), bitSerialInstruction)

    def isInputPort(self, portInfo):
        """Check if the PortInfo is an input port."""
        if isinstance(portInfo, PortInfo) and portInfo.isInputPort():
            self.ports.add(portInfo.getPortName())
            return True
        return False

    def isOutputPort(self, portInfo):
        """Check if the PortInfo is an output port."""
        if isinstance(portInfo, PortInfo) and portInfo.isOutputPort():
            self.ports.add(portInfo.getPortName())
            return True
        return False

    def isOutput(symbol):
        if "po" in symbol:
            return True
        else:
            return False

    def isInput(symbol):
        if "pi" in symbol:
            return True
        else:
            return False

    def isBitSerialRegister(symbol):
        pattern = r"^t[0-9]"
        return bool(re.match(pattern, symbol))

    def resolveOperand(self, symbol):
        # Lookup the symbol table
        val = self.symbolTable.getSymbol(symbol)
        if isinstance(val, LinkedInstruction):
            returnVal = None
           #  sourceInstruction = val.sourceInstructionList[0]
            # if sourceInstruction == None:
                # return None
            # sourceOperand = self.getDestinationOperandFromInstruction(sourceInstruction)

            # returnVal = self.resolveOperand(sourceOperand)
            # print(f"DEUBG: Return Symbol {returnVal}")
            # # Update the instruction.suspended based on the value of the resolved symbol
            # if isInput(returnVal) or isBitSerialRegister(returnVal):
                # print(f"DEUBG: Is input or bit-serial register\n")
                # val.unsuspend()
            # else:
                # # TODO
                # print(f"DEUBG: Is output or temp variable\n")
           #      returnVal = val
        else:
            returnVal = val
        return returnVal

    def transformLoadInstruction(self, statementIndex):
        riscvInstruction = self.riscvStatementList[statementIndex]
        portInfo = self.riscvStatementList[statementIndex + 1]
        destinationOperand = riscvInstruction.operandsList[0]
        sourceOperand = riscvInstruction.operandsList[1]
        suspended = False

        # Resolve register operand
        registerOperand = destinationOperand
        if "t" in registerOperand:
            suspended = False
        else:
            # Try to resolve the register, if not able mark this instruction as suspended
            resolvedOperand = self.resolveOperand(registerOperand)
            if resolvedOperand == None:
                suspended = True
            else:
                sourceOperand = resolvedOperand

        # Resolve reference operand
        referenceOperand = sourceOperand
        # Handle Input Load
        if self.isInputPort(portInfo):
            sourceOperand = portInfo.getPortName()  # Substitute the source operand with the input port name
            # Add referenceOperand:inputPort to the symbol table
            self.symbolTable.addSymbol(referenceOperand, sourceOperand)
        else:
            # Try to resolve the reference, if not able mark this instruction as unresolved
            resolvedOperand = self.resolveOperand(referenceOperand)
            if resolvedOperand == None:
                suspended = True
            else:
                sourceOperand = resolvedOperand

        self.appendBitSerialInstruction("read", [destinationOperand, sourceOperand], riscvInstruction.line, suspended)

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

    def transformStoreInstruction(self, statementIndex):
        riscvInstruction = self.riscvStatementList[statementIndex]
        portInfo = self.riscvStatementList[statementIndex + 1]
        destinationOperand = riscvInstruction.operandsList[1]
        sourceOperand = riscvInstruction.operandsList[0]

        suspended = False
        # Resolve register operand
        registerOperand = sourceOperand
        if not "t" in registerOperand:
            suspended = True
        else:
            # Try to resolve the register, if not able mark this instruction as unresolved
            # sourceOperand = self.resolveOperand(registerOperand)
            if sourceOperand == None:
                suspended = True


        # Resolve Reference operand
        referenceOperand = destinationOperand
        resolvedOperand = self.resolveOperand(destinationOperand)
        if resolvedOperand == None:
            suspended = True
        else:
            destinationOperand = resolvedOperand

        self.appendBitSerialInstruction("write", [sourceOperand, destinationOperand], riscvInstruction.line, suspended)

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
        newOpCode = self.getInstrunctionSequenceOpCode(instructionSequence)
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
        self.appendBitSerialInstruction(newOpCode, operandsList, line)

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
            self.appendBitSerialInstruction("write", writeOperandsList, line)

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

    def getInstrunctionSequenceOpCode(self, instructionSequence):
        transformationRules = {
            ('xor', 'not'): 'xnor',
            ('and', 'not'): 'nand',
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

