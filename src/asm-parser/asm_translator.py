#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: asm_translator.py
Description: Translates RISCV assembly code to bit-serial assembly code
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Author: Deyuan Guo <guodeyuan@gmail.com> - Analog PIM support
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
        sourceInstructionLinesStr = "X" if self.sourceInstructionList is None else \
            ', '.join(str(instr.line) if instr is not None else "-" for instr in self.sourceInstructionList)
        return f"{self.opCode:<10} {operandsListStr:<32} | Line {self.line}, SrcLines [{sourceInstructionLinesStr}], Suspended: {self.suspended}"

    def unsuspend(self):
        self.suspended = False

    def getOpCode(self):
        return self.opCode

    def getOperandsList(self):
        return self.operandsList

    def getSrcOperands(self):
        return AsmTranslator.getSrcOperands(self.opCode, self.operandsList)

    def getDestOperands(self):
        return AsmTranslator.getDestOperands(self.opCode, self.operandsList)

class SymbolTable:
    def __init__(self):
        self.dictionary = {}

    def getSymbol(self, key):
        # Return the value for the given key, or None if key doesn't exist
        return self.dictionary.get(key, None)

    def addSymbol(self, key, val):
        # Add the key-value pair to the dictionary
        self.dictionary[key] = val

    def __repr__(self):
        string = ""
        if not self.dictionary:
            return "Symbol table is empty."
        else:
            for key, val in self.dictionary.items():
                if isinstance(val, LinkedInstruction):
                    string += f"{key}: L{val.line}\n"
                else:
                    string += f"{key}: {val}\n"
        return string

    def print_symbols(self):
        print(self.__repr__())

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
        # Assumption: tempStr is in format temp%d
        index = int(tempStr[4:])
        # Set the element at the specified index to False
        if 0 <= index < len(self.isAllocated):
            self.isAllocated[index] = False
        else:
            raise IndexError("Index out of bounds")

class AsmTranslator:
    def __init__(self, riscvStatementList, inputList, outputList, pimMode, numRegs, debugLevel=0):
        self.riscvStatementList = riscvStatementList
        self.inputList = inputList
        self.outputList = outputList
        self.pimMode = pimMode
        self.numRegs = numRegs
        self.allRegs = set(([f't{i}' for i in range(7)] + [f's{i}' for i in range(12)])[:numRegs])
        self.debugLevel = debugLevel
        self.remainedOutputList = outputList.copy()
        self.bitSerialStatementList = []
        self.symbolTable = SymbolTable()
        self.resolvedInputList = []
        self.LINE_STRING = 80 * "=" + "\n"
        self.tempManager = TempManager()
        self.ports = set(inputList + outputList)

        if self.debugLevel >= 1:
            print("Starting AsmTranslator.")
            for i, input in enumerate(inputList):
                print(f'INPUT {i}: {input}')
            for i, output in enumerate(outputList):
                print(f'OUTPUT {i}: {output}')
            for i, statement in enumerate(riscvStatementList):
                print(f'[{i}] {statement}')
            print('-' * 40)

    def __get_statement_list_as_string(self, statement_list):
        return "\n".join([f"{statement}" for statement in statement_list])

    def __get_bit_serial_statement_list_string(self):
        return self.__get_statement_list_as_string(self.bitSerialStatementList)

    def __repr__(self):
        string = ""
        string += self.symbolTable.__repr__()
        string += self.LINE_STRING
        string += self.__get_bit_serial_statement_list_string()
        return string


    def translate(self):
        """ Translate the RISCV assembly to bit-serial assembly """
        print("Translating RISCV assembly to bit-serial assembly...\n")
        statementIndex = 0
        while statementIndex < len(self.riscvStatementList):
            statement = self.riscvStatementList[statementIndex]
            if isinstance(statement, Instruction):
                if len(self.remainedOutputList) == 0:
                    if self.debugLevel >= 1:
                        print("Bit-Serial Assembly Code After Translation:")
                        for i, instruction in enumerate(self.bitSerialStatementList):
                            print(f"[{i}] {instruction}")
                    return
                elif statement.isLoadInstruction():
                    statementIndex += self.translateLoadInstruction(statementIndex)
                elif statement.isStoreInstruction():
                    statementIndex += self.translateStoreInstruction(statementIndex)
                elif statement.isMoveInstruction():
                    statementIndex += self.translateMoveInstruction(statementIndex)
                else:
                    if self.debugLevel >= 2:
                        print(f"DEBUG: IDX {statementIndex:<5} {'INST-IGNOR':<10} : {self.riscvStatementList[statementIndex]}")
                    statementIndex += 1
            elif isinstance(statement, Directive) and statement.val == "#APP":
                statementIndex += self.translateInlineAssembly(statementIndex)
            else:
                if self.debugLevel >= 2:
                    print(f"DEBUG: IDX {statementIndex:<5} {'STMT-IGNOR':<10} : {self.riscvStatementList[statementIndex]}")
                statementIndex += 1

    def shrink_temp_variables(self):
        """ Shrink temporary variables in the bit-serial statement list """
        print("Simplifying temporary variables in the bit-serial assembly...\n")
        tempVariablesShrinker = TempVariablesShrinker(self.bitSerialStatementList, self.allRegs, self.debugLevel)
        tempVariablesShrinker.shrinkTempVariables()
        self.bitSerialStatementList = tempVariablesShrinker.newInstructionSequence

        if self.debugLevel >= 1:
            print("Bit-Serial Assembly Code:")
            for i, instruction in enumerate(self.bitSerialStatementList):
                print(f"[{i}] {instruction}")
            print("Symbol Table:")
            self.symbolTable.print_symbols()
            print('-' * 40)

    def getDestinationOperandFromInstruction(self, instruction):
        destOperands = instruction.getDestOperands()
        return destOperands[0] if destOperands else None

    def getSourceOperandFromInstruction(self, instruction):
        srcOperands = instruction.getSrcOperands()
        return srcOperands[0] if srcOperands else None

    @staticmethod
    def getSrcOperands(opCode, operandsList):
        if opCode == "write":
            return [operandsList[0]]
        elif opCode.startswith("maj3"):
            return operandsList[-3:]
        else:
            return operandsList[1:]

    @staticmethod
    def getDestOperands(opCode, operandsList):
        """ Get all destination operands based on opCode and operandsList """
        if opCode == "write":
            return [operandsList[1]]
        elif opCode.startswith("maj3"):
            return operandsList[:-3]  # There can be multiple dest operands of maj3 in analog PIM
        else:
            return [operandsList[0]]

    def appendBitSerialInstruction(self, opCode, operands, line, suspended=False):
        # Identify source instructions
        srcOperands = self.getSrcOperands(opCode, operands)
        sourceInstructionList = [self.symbolTable.getSymbol(srcOperand) for srcOperand in srcOperands]
        # Create a new instruction
        bitSerialInstruction = LinkedInstruction(opCode, operands, line, sourceInstructionList=sourceInstructionList, suspended=suspended)
        self.bitSerialStatementList.append(bitSerialInstruction)
        # Note: Handle multiple dest operands of inline asm block
        destOperands = self.getDestOperands(opCode, operands)
        for destOperand in destOperands:
            self.symbolTable.addSymbol(destOperand, bitSerialInstruction)
            if opCode == "write" and destOperand in self.remainedOutputList:
                self.remainedOutputList.remove(destOperand)

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
        return symbol in self.allRegs

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
                    raise Exception("Unhandled condition.")
            return returnVal, doUnsudpendThePath

        else:
            returnVal, doUnsudpendThePath = self.resolveOperand(destinationOperand)
            if "temp" in self.getDestinationOperandFromInstruction(instruction):
                if "temp" not in self.getSourceOperandFromInstruction(instruction):
                    instruction.unsuspend()
                    doUnsudpendThePath = True

            return returnVal, doUnsudpendThePath

    def translateMoveInstruction(self, statementIndex):
        """ Translate a move instruction in RISCV assembly to bit-serial assembly """
        if self.debugLevel >= 2:
            print(f"DEBUG: IDX {statementIndex:<5} {'MOVE':<10} : {self.riscvStatementList[statementIndex]}")

        riscvInstruction = self.riscvStatementList[statementIndex]
        if self.isBitSerialRegister(riscvInstruction.operandsList[0]):
            if self.isBitSerialRegister(riscvInstruction.operandsList[1]):
                sourceOperand = riscvInstruction.operandsList[1]
                destinationOperand = riscvInstruction.operandsList[0]
                self.appendBitSerialInstruction("mv", [destinationOperand, sourceOperand], riscvInstruction.line, suspended=False)
            else:
                sourceOperand, doUnsudpendThePath = self.resolveOperand(riscvInstruction.operandsList[1], line=riscvInstruction.line)
                if sourceOperand == None:
                    return 1
                destinationOperand = riscvInstruction.operandsList[0]
                self.appendBitSerialInstruction("read", [destinationOperand, sourceOperand], riscvInstruction.line, suspended=False)
        else:
            if self.isBitSerialRegister(riscvInstruction.operandsList[1]):
                raise Exception(f"Unhandled move instruction at line {riscvInstruction.line} in the RISCV assembly.")
            else:
                # Ignore this instruction
                return 1
        return 1

    def translateLoadInstruction(self, statementIndex):
        """ Translate a load instruction from RISCV assembly to bit-serial assembly """
        if self.debugLevel >= 2:
            print(f"DEBUG: IDX {statementIndex:<5} {'LOAD':<10} : {self.riscvStatementList[statementIndex]}")

        riscvInstruction = self.riscvStatementList[statementIndex]
        portInfo = self.riscvStatementList[statementIndex + 1]

        sourceOperand = self.resolveSourceOperandForLoad(riscvInstruction.operandsList[1], portInfo, line=riscvInstruction.line)
        destinationOperand, suspended = self.resolveDestinationOperand(riscvInstruction.operandsList[0], sourceOperand, line=riscvInstruction.line)

        if destinationOperand and sourceOperand:
            self.appendBitSerialInstruction("read", [destinationOperand, sourceOperand], riscvInstruction.line, suspended)
        else:
            if self.debugLevel >= 2:
                print(f"WARNING: Invalid load instruction at line {riscvInstruction.line}.")

        return 1

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
        """ Translate a store instruction in RISCV assembly to bit-serial assembly """
        if self.debugLevel >= 2:
            print(f"DEBUG: IDX {statementIndex:<5} {'STORE':<10} : {self.riscvStatementList[statementIndex]}")

        riscvInstruction = self.riscvStatementList[statementIndex]
        portInfo = self.riscvStatementList[statementIndex + 1]

        sourceOperand = self.resolveSourceOperandForStore(riscvInstruction.operandsList[0])
        destinationOperand = self.mapToTemporaryVariable(riscvInstruction.operandsList[1])

        self.handlePointerOperation(sourceOperand, destinationOperand)

        suspended = True
        self.appendBitSerialInstruction("write", [sourceOperand, destinationOperand], riscvInstruction.line, suspended)

        return 1

    def resolveSourceOperandForStore(self, sourceOperand):
        if not self.isBitSerialRegister(sourceOperand):
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
        if self.isBitSerialRegister(sourceOperand) and "temp" in destinationOperand:
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

    def handleWriteToOutputPort(self, statementIndex, instructionSequence, line):
        """Handle writing to an output port after inline assembly."""
        portInfoIndex = statementIndex + len(instructionSequence) + 2

        # Search for output port in the debugging information
        while isinstance(self.riscvStatementList[portInfoIndex], PortInfo):
            portInfo = self.riscvStatementList[portInfoIndex]
            if self.isOutputPort(portInfo):
                # TODO: Remove this assumption that the first operand of the last instruction
                #       in an asm block is the destination operand. This creates a special
                #       requirement to the asm generator in BLIF translator.
                destinationOperand = instructionSequence[-1].operandsList[0]
                writeSourceOperand = destinationOperand
                writeDestinationOperand = portInfo.getPortName()
                writeOpCode = "write"
                writeOperandsList = [writeSourceOperand, writeDestinationOperand]
                self.appendBitSerialInstruction("write", writeOperandsList, line)
                self.symbolTable.addSymbol(writeSourceOperand, writeDestinationOperand)
                return
            portInfoIndex += 1

    def parsePimOpDirective(self, statementIndex):
        """ Parse the #PIM_OP directive in inline asm block and return the opcode and operands """
        # Note: BLIF translator passes #PIM_OP info as inline assembly comments
        pimOpDirective = self.riscvStatementList[statementIndex]
        pimOpInfo = pimOpDirective.val.split()
        if len(pimOpInfo) < 3 or pimOpInfo[0] != '#PIM_OP':
            raise Exception(f"Error: Unexpected '#PIM_OP' directive at line {pimOpDirective.line}: '{pimOpInfo}'")
        if pimOpInfo[1] in ['BEGIN', 'END']:
            return None, []  # Ignore BEGIN/END markers
        newOpCode = pimOpInfo[2]
        operandsList = pimOpInfo[3:]
        #print(f"DEBUG PIM_OP: {newOpCode}, {operandsList} at line {pimOpDirective.line}")
        return newOpCode, operandsList

    def translateInlineAssembly(self, statementIndex):
        """ Translate an inline assembly block between #APP and #NO_APP directives """
        if self.debugLevel >= 2:
            print(f"DEBUG: IDX {statementIndex:<5} {'INLINE-ASM':<10} : {self.riscvStatementList[statementIndex]}")
        newOpCode, operandsList = self.parsePimOpDirective(statementIndex + 1)
        if newOpCode is None:
            return 2

        statementIndex += 1
        instructionSequence = self.getInlineInstructionSequence(statementIndex)
        firstRiscvInstruction = instructionSequence[0]

        # Handle the mapped bit-serial instruction
        self.appendBitSerialInstruction(newOpCode, operandsList, firstRiscvInstruction.line)

        # Handle write to output port if necessary
        self.handleWriteToOutputPort(statementIndex, instructionSequence, firstRiscvInstruction.line)

        return len(instructionSequence) + 2

    def getBitSerialAsm(self):
        return self.bitSerialStatementList

class TempVariablesShrinker:
    """ Shrinks temporary variables to use the smallest set of indices """

    def __init__(self, instructionSequence, pimRegs, debugLevel=0):
        self.instructionSequence = instructionSequence
        self.pimRegs = pimRegs
        self.debugLevel = debugLevel
        self.newInstructionSequence = []
        self.symbolTable = SymbolTable()
        self.tempManager = TempManager()

    def shrinkTempVariables(self):
        for instruction in self.instructionSequence:
            operandIdx = 0
            hasPimReg = False
            for operand in instruction.operandsList:
                if not instruction.suspended:
                    if "temp" in operand:
                        newOperand = self.updateTempVariable(operand)
                        instruction.operandsList[operandIdx] = newOperand
                if operand in self.pimRegs:
                    hasPimReg = True
                operandIdx += 1
            if not instruction.suspended:
                self.newInstructionSequence.append(instruction)
            elif hasPimReg:
                if self.debugLevel >= 1:
                    print(f'Warning: Suspended instruction with PIM register found: {instruction}')

    def updateTempVariable(self, tempVariable):
        avaialableTempVariable = self.symbolTable.getSymbol(tempVariable)
        if avaialableTempVariable == None:
            newTempVariable = f"temp{self.tempManager.newTemp()}"
            self.symbolTable.addSymbol(tempVariable, newTempVariable)
            return newTempVariable
        else:
            return avaialableTempVariable

