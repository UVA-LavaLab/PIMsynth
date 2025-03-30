#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: asm_translator.py
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
            sourceInstructionLines = [(str(instruction.line) if instruction != None else "-") for instruction in self.sourceInstructionList]
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

class AsmTranslator:
    def __init__(self, riscvStatementList, inputList, outputList):
        self.riscvStatementList = riscvStatementList
        self.inputList = inputList
        self.outputList = outputList
        self.bitSerialStatementList = []
        self.symbolTable = SymbolTable()
        self.resolvedInputList = []
        self.tempManager = TempManager()
        self.ports = set(inputList + outputList)
        self.translate()
        tempVariablesShrinker = TempVariablesShrinker(self.bitSerialStatementList)
        # tempVariablesShrinker.shrinkTempVariables()
        self.bitSerialStatementList = tempVariablesShrinker.newInstructionSequence

    def translate(self):
        for statementIndex, statement in enumerate(self.riscvStatementList):
            if isinstance(statement, Instruction):
                if statement.isLoadInstruction():
                    self.translateLoadInstruction(statementIndex)
                    continue
                if statement.isStoreInstruction():
                    self.translateStoreInstruction(statementIndex)
                    continue
                if statement.isMoveInstruction():
                    self.translateMoveInstruction(statementIndex)
                    continue
            elif isinstance(statement, Directive) and statement.val == "#APP":
                self.translateInlineAssembly(statementIndex)

    def getDestinationOperandFromInstruction(self, instruction):
        if instruction.opCode == "write":
            return instruction.operandsList[1]
        else:
            return instruction.operandsList[0]

    def getSourceOperandFromInstruction(self, instruction):
        if instruction.opCode == "write":
            return instruction.operandsList[0]
        else:
            return instruction.operandsList[1]

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
        if isinstance(portInfo, PortInfo) and portInfo.isInputPort(self.inputList):
            return True
        return False

    def isOutputPort(self, portInfo):
        """Check if the PortInfo is an output port."""
        if isinstance(portInfo, PortInfo) and portInfo.isOutputPort(self.outputList):
            return True
        return False

    def isOutput(self, symbol):
        return symbol in self.outputList

    def isInput(self, symbol):
        return symbol in self.inputList

    def isBitSerialRegister(self, symbol):
        pattern = r"^t[0-9]"
        return bool(re.match(pattern, symbol))

    def resolveOperand(self, symbol, line=-1):
        # Lookup the symbol table
        val = self.symbolTable.getSymbol(symbol)
        returnVal = "XXX"
        doUnsudpendThePath = False

        if isinstance(val, str):
            returnVal, doUnsudpendThePath = self.resolveTemp(val, line=line)

        elif isinstance(val, LinkedInstruction):
            returnVal, doUnsudpendThePath = self.resolveLinkedInstruction(val, line=line)
        else:
            returnVal = val

        return returnVal, doUnsudpendThePath

    def resolveTemp(self, temp, line=-1):
        if "temp" in temp:
            return self.resolveOperand(temp, line=line)
        return temp, False

    def resolveLinkedInstruction(self, instruction, line=-1):
        sourceInstruction = instruction.sourceInstructionList[0]
        if sourceInstruction is None:
            if self.isBitSerialRegister(self.getSourceOperandFromInstruction(instruction)):
                return self.getDestinationOperandFromInstruction(instruction), False
            else:
                return self.getSourceOperandFromInstruction(instruction), False

        destinationOperand = self.getDestinationOperandFromInstruction(sourceInstruction)
        sourceOperand = self.getSourceOperandFromInstruction(sourceInstruction)
        if self.isBitSerialRegister(destinationOperand):
            if "temp" in self.getDestinationOperandFromInstruction(instruction):
                if self.isInput(sourceOperand):
                    doUnsudpendThePath = False
                    returnVal = sourceOperand
                elif "temp" not in self.getSourceOperandFromInstruction(instruction):
                    instruction.unsuspend()
                    doUnsudpendThePath = True
                    returnVal = self.getDestinationOperandFromInstruction(instruction)
                else:
                    raise Error("Unhandled condition.")
            return returnVal, doUnsudpendThePath

        else:
            returnVal, doUnsudpendThePath = self.resolveOperand(destinationOperand)
            if "temp" in self.getDestinationOperandFromInstruction(instruction):
                if "temp" not in self.getSourceOperandFromInstruction(instruction):
                    instruction.unsuspend()
                    doUnsudpendThePath = True

            return returnVal, doUnsudpendThePath

    def translateMoveInstruction(self, statementIndex):
        riscvInstruction = self.riscvStatementList[statementIndex]
        if self.isBitSerialRegister(riscvInstruction.operandsList[0]):
            if self.isBitSerialRegister(riscvInstruction.operandsList[1]):
                sourceOperand = riscvInstruction.operandsList[1]
                destinationOperand = riscvInstruction.operandsList[0]
                self.appendBitSerialInstruction("move", [destinationOperand, sourceOperand], riscvInstruction.line, suspended=False)
            else:
                sourceOperand, doUnsudpendThePath = self.resolveOperand(riscvInstruction.operandsList[1], line=riscvInstruction.line)
                destinationOperand = riscvInstruction.operandsList[0]
                self.appendBitSerialInstruction("read", [destinationOperand, sourceOperand], riscvInstruction.line, suspended=False)
        else:
            if self.isBitSerialRegister(riscvInstruction.operandsList[1]):
                raise Error("Unhandled move instruction at line {riscvInstruction.line} in the RISCV assembly.")
            else:
                raise Error("Unhandled move instruction at line {riscvInstruction.line} in the RISCV assembly.")

    def translateLoadInstruction(self, statementIndex):
        riscvInstruction = self.riscvStatementList[statementIndex]
        portInfo = self.riscvStatementList[statementIndex + 1]

        sourceOperand = self.resolveSourceOperandForLoad(riscvInstruction.operandsList[1], portInfo, line=riscvInstruction.line)
        destinationOperand, suspended = self.resolveDestinationOperand(riscvInstruction.operandsList[0], sourceOperand, line=riscvInstruction.line)

        if destinationOperand and sourceOperand:
            self.appendBitSerialInstruction("read", [destinationOperand, sourceOperand], riscvInstruction.line, suspended)

    def resolveDestinationOperand(self, destinationOperand, sourceOperand, line=-1):
        if self.isBitSerialRegister(destinationOperand):
            return destinationOperand, False  # Not suspended

        if not self.isInput(sourceOperand):
            resolvedOperand = self.symbolTable.getSymbol(destinationOperand)
            if resolvedOperand is None:
                tempVariable = f"temp{self.tempManager.newTemp()}"
                self.symbolTable.addSymbol(destinationOperand, tempVariable)
                resolvedOperand = tempVariable
                if "temp" in resolvedOperand:
                    return None, True  # Invalid operand, mark as suspended
            elif "temp" in resolvedOperand:
                if sourceOperand is None:
                    return None, True
                elif "temp" in sourceOperand:
                    return None, True
                else:
                    return resolvedOperand, True

        else:
            tempVariable = f"temp{self.tempManager.newTemp()}"
            self.symbolTable.addSymbol(destinationOperand, tempVariable)
            resolvedOperand = tempVariable
            return resolvedOperand, True


        return resolvedOperand, False

    def resolveSourceOperandForLoad(self, sourceOperand, portInfo, line=-1):
        if self.isInputPort(portInfo):
            if not portInfo.getPortName() in self.resolvedInputList:
                self.resolvedInputList.append(portInfo.getPortName())
                return portInfo.getPortName()  # Use input port name

        resolvedOperand, doUnsudpendThePath = self.resolveOperand(sourceOperand, line=line)
        return resolvedOperand

    def translateStoreInstruction(self, statementIndex):
        riscvInstruction = self.riscvStatementList[statementIndex]
        portInfo = self.riscvStatementList[statementIndex + 1]

        sourceOperand = self.resolveSourceOperandForStore(riscvInstruction.operandsList[0])
        destinationOperand = self.mapToTemporaryVariable(riscvInstruction.operandsList[1])

        self.handlePointerOperation(sourceOperand, destinationOperand)

        suspended = True
        self.appendBitSerialInstruction("write", [sourceOperand, destinationOperand], riscvInstruction.line, suspended)

    def resolveSourceOperandForStore(self, sourceOperand):
        if "t" not in sourceOperand:
            resolvedOperand = self.symbolTable.getSymbol(sourceOperand)
            if resolvedOperand is None:
                tempVariable = f"temp{self.tempManager.newTemp()}"
                self.symbolTable.addSymbol(sourceOperand, tempVariable)
                resolvedOperand = tempVariable
            return resolvedOperand
        return sourceOperand

    def mapToTemporaryVariable(self, referenceOperand):
        tempVariable = f"temp{self.tempManager.newTemp()}"
        self.symbolTable.addSymbol(referenceOperand, tempVariable)
        return tempVariable

    def handlePointerOperation(self, sourceOperand, destinationOperand):
        if "t" in sourceOperand and "temp" in destinationOperand:
            value = self.symbolTable.getSymbol(sourceOperand)
            if isinstance(value, str) and self.isOutput(value):
                self.symbolTable.removeSymbol(sourceOperand)
                self.symbolTable.addSymbol(destinationOperand, value)

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
            # print(f"Info: No mapped opcode found for inline assembly at line {line}.")
            pass
        else:
            # print(f"Info: Mapped opcode for the line {line} is {newOpCode}.")
            pass
        return newOpCode

    def handleBitSerialInstruction(self, instructionSequence, newOpCode, firstRiscvInstruction):
        """Handle the translation of the bit-serial instruction from inline assembly."""
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
            self.symbolTable.addSymbol(writeSourceOperand, writeDestinationOperand)

    def translateInlineAssembly(self, statementIndex):
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
        """Check if a given sequence of opcodes matches the translation rule."""
        if len(instructionSequence) < len(sequence):
            return False

        return all(
            instructionSequence[i].opCode == sequence[i]
            for i in range(len(sequence))
        )

    def getInstrunctionSequenceOpCode(self, instructionSequence):
        translationRules = {
            ('xor', 'not'): 'xnor',
            ('and', 'not'): 'nand',
        }
        mappedOpcodes = []  # To store the mapped opcodes
        i = 0
        while i < len(instructionSequence):
            matched = False
            currentOp = instructionSequence[i].opCode

            # Try to match a sequence starting at the current position
            for sequence, targetOpcode in translationRules.items():
                seqLen = len(sequence)

                # Check if we have enough instructions remaining and the sequence matches
                if i + seqLen <= len(instructionSequence) and all(
                    instructionSequence[i + j].opCode == sequence[j] for j in range(seqLen)
                ):
                    mappedOpcodes.append(targetOpcode)
                    i += seqLen  # Skip the instructions that are part of the matched sequence
                    matched = True
                    break

            # If no translation rule matched, just add the current opcode
            if not matched:
                mappedOpcodes.append(currentOp)
                i += 1

        if len(mappedOpcodes) == 1:
            return mappedOpcodes[0]
        else:
            return None

    def getBitSerialAsm(self):
        return self.bitSerialStatementList

class TempVariablesShrinker:
    def __init__(self, instructionSequence):
        self.instructionSequence = instructionSequence
        self.newInstructionSequence = []
        self.symbolTable = SymbolTable()
        self.tempManager = TempManager()

    def shrinkTempVariables(self):
        for instruction in self.instructionSequence:
            operandIdx = 0
            for operand in instruction.operandsList:
                if not instruction.suspended:
                    if "temp" in operand:
                        newOperand = self.updateTempVariable(operand)
                        instruction.operandsList[operandIdx] = newOperand
                operandIdx += 1
            if not instruction.suspended:
                self.newInstructionSequence.append(instruction)

    def updateTempVariable(self, tempVariable):
        avaialableTempVariable = self.symbolTable.getSymbol(tempVariable)
        if avaialableTempVariable == None:
            newTempVariable = f"temp{self.tempManager.newTemp()}"
            self.symbolTable.addSymbol(tempVariable, newTempVariable)
            return newTempVariable
        else:
            return avaialableTempVariable

