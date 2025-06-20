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

    def get_opcode(self):
        return self.opCode

    def get_src_operands(self):
        return self.get_src_operands_from_opcode(self.opCode, self.operandsList)

    def get_dest_operands(self):
        return self.get_dest_operands_from_opcode(self.opCode, self.operandsList)

    @staticmethod
    def get_src_operands_from_opcode(opcode, operands_list):
        if opcode == "write":
            return [operands_list[0]]
        elif opcode.startswith("maj3"):
            return operands_list[-3:]
        elif opcode in ["copy", "mv"]:
            return operands_list[-1:]
        elif opcode in ["zero", "one"]:
            return []
        else:
            return operands_list[1:]

    @staticmethod
    def get_dest_operands_from_opcode(opcode, operands_list):
        """ Get all destination operands based on opCode and operandsList """
        # In analog PIM, there can be multiple dest operands for maj/copy/mv/zero/one
        if opcode == "write":
            return [operands_list[1]]
        elif opcode.startswith("maj3"):
            return operands_list[:-3]
        elif opcode in ["copy", "mv"]:
            return operands_list[:-1]
        elif opcode in ["zero", "one"]:
            return operands_list
        else:
            return [operands_list[0]]


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
        string = "Symbol Table:\n"
        if not self.dictionary:
            return "Symbol table is empty."
        else:
            for key, val in self.dictionary.items():
                if isinstance(val, LinkedInstruction):
                    string += f"    {key:<10} : L{val.line}\n"
                else:
                    string += f"    {key:<10} : {val}\n"
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

    def __get_bit_serial_statement_list_string(self):
        string = "Bit-Serial Assembly Code:\n"
        for i, statement in enumerate(self.bitSerialStatementList):
            string += f"[{i}] {statement}\n"
        return string

    def __repr__(self):
        string = ""
        string += self.LINE_STRING
        string += self.symbolTable.__repr__()
        string += self.LINE_STRING
        string += self.__get_bit_serial_statement_list_string()
        string += self.LINE_STRING
        return string


    def translate(self):
        """ Translate the RISCV assembly to bit-serial assembly """
        print("Translating RISCV assembly to bit-serial assembly...")
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

    def post_translation_optimization(self):
        """ Perform post-translation optimizations on the bit-serial assembly """
        # Post translation optimization
        self.shrink_temp_variables()
        self.remove_redundant_copies()
        self.simplify_port_spills()
        self.shrink_temp_variables()
        self.pack_analog_copies()

    def shrink_temp_variables(self):
        """ Shrink temporary variables in the bit-serial statement list """
        print("INFO: Simplifying temporary variables in the bit-serial assembly...")
        temp_var_shrinker = TempVariablesShrinker(self.bitSerialStatementList, self.pimMode, self.allRegs, self.debugLevel)
        temp_var_shrinker.shrink_temp_variables()
        self.bitSerialStatementList = temp_var_shrinker.new_instruction_sequence
        if self.debugLevel >= 1:
            print(self)

    def remove_redundant_copies(self):
        """ Remove redundant copy instructions in the bit-serial statement list """
        print("INFO: Removing redundant copy instructions...")
        copy_remover = RedundantCopyRemover(self.bitSerialStatementList, self.pimMode, self.debugLevel)
        copy_remover.remove_redendant_copies()
        self.bitSerialStatementList = copy_remover.new_instruction_sequence
        if self.debugLevel >= 1:
            print(self)

    def simplify_port_spills(self):
        """ Simplify port spills in the bit-serial statement list """
        print("INFO: Simplifying port spills in the bit-serial assembly...")
        port_spill_simplifier = PortSpillSimplifier(self.bitSerialStatementList, self.pimMode, self.inputList, self.outputList, self.debugLevel)
        port_spill_simplifier.simplify_port_spills()
        self.bitSerialStatementList = port_spill_simplifier.new_instruction_sequence
        if self.debugLevel >= 1:
            print(self)

    def pack_analog_copies(self):
        """ Pack analog copies of port/zero/one instructions for analog PIM mode """
        if self.pimMode != "analog":
            return
        print("INFO: Packing analog copies of port/zero/one instructions...")
        analog_copy_packer = AnalogCopyPacker(self.bitSerialStatementList, self.pimMode, self.debugLevel)
        analog_copy_packer.pack_analog_copies()
        self.bitSerialStatementList = analog_copy_packer.new_instruction_sequence
        if self.debugLevel >= 1:
            print(self)

    def getDestinationOperandFromInstruction(self, instruction):
        destOperands = instruction.get_dest_operands()
        return destOperands[0] if destOperands else None

    def getSourceOperandFromInstruction(self, instruction):
        srcOperands = instruction.get_src_operands()
        return srcOperands[0] if srcOperands else None

    def appendBitSerialInstruction(self, opCode, operands, line, suspended=False):
        # Identify source instructions
        srcOperands = LinkedInstruction.get_src_operands_from_opcode(opCode, operands)
        sourceInstructionList = [self.symbolTable.getSymbol(srcOperand) for srcOperand in srcOperands]
        # Create a new instruction
        bitSerialInstruction = LinkedInstruction(opCode, operands, line, sourceInstructionList=sourceInstructionList, suspended=suspended)
        self.bitSerialStatementList.append(bitSerialInstruction)
        # Note: Handle multiple dest operands of inline asm block
        destOperands = LinkedInstruction.get_dest_operands_from_opcode(opCode, operands)
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


class PostTranslationOptimizer:
    """ Base class for post-translation optimizers """

    def __init__(self, instruction_sequence, pim_mode, debug_level=0):
        self.instruction_sequence = instruction_sequence
        self.pim_mode = pim_mode
        self.debug_level = debug_level
        self.new_instruction_sequence = []
        self.line_map = {}

    def update_line_map(self, removed_line, source_insts):
        """ Record the mapping from removed lines to their source lines """
        if len(source_insts) != 1:
            raise ValueError(f"Not supported: Remove an inst with multiple sources at line {removed_line}.")
        src_inst = source_insts[0]
        if src_inst.line in self.line_map:
            src_inst = self.line_map[src_inst.line]  # use root
        self.line_map[removed_line] = src_inst

    def update_source_lines(self, inst):
        """ Update the source lines of an instruction """
        for idx, src_inst in enumerate(inst.sourceInstructionList):
            if src_inst is not None and src_inst.line in self.line_map:
                inst.sourceInstructionList[idx] = self.line_map[src_inst.line]


class TempVariablesShrinker(PostTranslationOptimizer):
    """ Shrinks temporary variables to use the smallest set of indices """

    def __init__(self, instruction_sequence, pim_mode, pim_regs, debug_level=0):
        super().__init__(instruction_sequence, pim_mode, debug_level)
        self.pim_regs = pim_regs
        self.symbol_table = SymbolTable()
        self.temp_manager = TempManager()

    def shrink_temp_variables(self):
        for instruction in self.instruction_sequence:
            operand_idx = 0
            has_pim_reg = False
            for operand in instruction.operandsList:
                if not instruction.suspended:
                    if "temp" in operand:
                        newOperand = self.update_temp_variable(operand)
                        instruction.operandsList[operand_idx] = newOperand
                if operand in self.pim_regs:
                    has_pim_reg = True
                operand_idx += 1
            if not instruction.suspended:
                self.new_instruction_sequence.append(instruction)
            elif has_pim_reg:
                if self.debug_level >= 1:
                    print(f'Warning: Suspended instruction with PIM register found: {instruction}')

    def update_temp_variable(self, temp_variable):
        avaialable_temp_variable = self.symbol_table.getSymbol(temp_variable)
        if avaialable_temp_variable == None:
            new_temp_variable = f"temp{self.temp_manager.newTemp()}"
            self.symbol_table.addSymbol(temp_variable, new_temp_variable)
            return new_temp_variable
        else:
            return avaialable_temp_variable


class RedundantCopyRemover(PostTranslationOptimizer):
    """ Remove redundant copy/move instructions from the instruction sequence """

    def __init__(self, instruction_sequence, pim_mode, debug_level=0):
        super().__init__(instruction_sequence, pim_mode, debug_level)

    def remove_redendant_copies(self):
        removed_count = 0
        for i, inst in enumerate(self.instruction_sequence):
            if inst.suspended:
                continue
            if inst.get_opcode() in ["copy", "mv"] and inst.get_src_operands() == inst.get_dest_operands():
                inst.suspended = True  # Mark the instruction as suspended
                self.update_line_map(inst.line, inst.sourceInstructionList)
                removed_count += 1
            else:
                self.update_source_lines(inst)
                self.new_instruction_sequence.append(inst)
        print(f"INFO: Summary: Removed {removed_count} redundant copies.")


class PortSpillSimplifier(PostTranslationOptimizer):
    """ Simpify port spill instructions """

    def __init__(self, instruction_sequence, pim_mode, input_ports, output_ports, debug_level=0):
        super().__init__(instruction_sequence, pim_mode, debug_level)
        self.input_ports = input_ports
        self.output_ports = output_ports
        self.symbol_inst_map = SymbolTable()
        self.symbol_port_map = SymbolTable()
        self.symbol_trace = {}  # linenum -> { operand : linked instruction, ... }

    def simplify_port_spills(self):
        removed_count = 0
        # 1st pass: Replace read temp var with input port if possible
        for i, inst in enumerate(self.instruction_sequence):
            if inst.suspended:
                continue
            self.update_symbol_inst_map(inst)
            self.update_symbol_port_map(inst)
            # print(f"DEBUG: Processing instruction {i}: {inst}")
            # self.debug_print()
            self.replace_temp_var_with_in_port(inst)
        # 2nd pass: Suspend unneeded instructions
        line_deps = set()
        for i, inst in reversed(list(enumerate(self.instruction_sequence))):
            if inst.suspended:
                continue
            line = inst.line
            to_keep = bool(line in line_deps)
            if not to_keep and inst.get_opcode() == "write":
                if len(inst.get_dest_operands()) == 1 and inst.get_dest_operands()[0] in self.output_ports:
                    to_keep = True
            if to_keep:
                for src_inst in inst.sourceInstructionList:
                    if src_inst is not None:
                        line_deps.add(src_inst.line)
                continue
            # Suspend the instruction
            inst.suspended = True
            removed_count += 1
        # 3rd pass: Update the final instruction sequence
        for inst in self.instruction_sequence:
            if not inst.suspended:
                self.new_instruction_sequence.append(inst)
        print(f"INFO: Summary: Removed {removed_count} read/write from port spill simplification.")

    def debug_print(self):
        """ Print debug information """
        print("Symbol Trace:")
        for line, item in self.symbol_trace.items():
            string = f"Line {line}: "
            for operand, inst in item.items():
                if inst is not None:
                    string += f"{operand} -> {inst.line}, "
                else:
                    string += f"{operand} -> None, "
            print(string[:-2])  # Remove the last comma and space
        print("Symbol Inst Map:")
        self.symbol_inst_map.print_symbols()
        print("Symbol Port Map:")
        self.symbol_port_map.print_symbols()

    def update_symbol_inst_map(self, inst):
        """ Update symbol to inst map """
        line = inst.line
        self.symbol_trace.setdefault(line, {})
        # Add dest operands
        for dest in inst.get_dest_operands():
            self.symbol_inst_map.addSymbol(dest, inst)
            self.symbol_trace[line][dest] = inst
        # Add src operands for analog PIM
        opcode = inst.get_opcode()
        if self.pim_mode == "analog" and (opcode in ["and2", "or2"] or opcode.startswith("maj3")):
            for src in inst.get_src_operands():
                self.symbol_inst_map.addSymbol(src, inst)
                self.symbol_trace[line][src] = inst
        else:
            for src in inst.get_src_operands():
                if self.symbol_inst_map.getSymbol(src) is not None:
                    self.symbol_trace[line][src] = self.symbol_inst_map.getSymbol(src)
                else:
                    self.symbol_trace[line][src] = None

    def update_symbol_port_map(self, inst):
        """ Update symbol to port map """
        # Map symbol to input port operands if applicable
        opcode = inst.get_opcode()
        if opcode == "write":
            if len(inst.get_src_operands()) == 1:
                operand_to_trace = inst.get_src_operands()[0]
                operand_to_be_replaced = inst.get_dest_operands()[0]
                in_port = self.trace_in_port_operand(inst.line, operand_to_trace)
                if in_port:
                    self.symbol_port_map.addSymbol(operand_to_be_replaced, in_port)
                elif self.symbol_port_map.getSymbol(operand_to_be_replaced) is not None:
                    self.symbol_port_map.removeSymbol(operand_to_be_replaced)

    def trace_in_port_operand(self, line, symbol):
        """ Trace the input port operand if symbol is an alias of it """
        if self.symbol_trace[line] is None or symbol not in self.symbol_trace[line]:
            return None
        pred_inst = self.symbol_trace[line][symbol]
        while pred_inst is not None:
            if pred_inst.get_opcode() == "read":
                if len(pred_inst.get_src_operands()) == 1 and pred_inst.get_src_operands()[0] in self.input_ports:
                    return pred_inst.get_src_operands()[0]
            elif pred_inst.get_opcode() == "write":
                if len(pred_inst.get_src_operands()) == 1 and pred_inst.get_dest_operands()[0] in self.input_ports:
                    return pred_inst.get_dest_operands()[0]
            elif pred_inst.get_opcode() in ["copy", "mv"]:
                if len(pred_inst.get_src_operands()) == 1:
                    pred_line = pred_inst.line
                    pred_operand = pred_inst.get_src_operands()[0]
                    pred_inst = self.symbol_trace[pred_line][pred_operand]
                    continue
            break
        return None

    def replace_temp_var_with_in_port(self, inst):
        """ Replace temporary variable with input port if possible """
        if inst.get_opcode() == "read":
            if len(inst.get_src_operands()) == 1:
                operand_to_be_replaced = inst.get_src_operands()[0]
                operand_to_use = self.symbol_port_map.getSymbol(operand_to_be_replaced)
                if operand_to_use is not None:
                    inst.operandsList[1] = operand_to_use
                    inst.sourceInstructionList = [None]
                    if self.debug_level >= 4:
                        print(f"DEBUG: After replacement: {inst}")


class AnalogCopyPacker(PostTranslationOptimizer):
    """ Pack analog copies of port/zero/one instructions for analog PIM mode """

    def __init__(self, instruction_sequence, pim_mode, debug_level=0):
        super().__init__(instruction_sequence, pim_mode, debug_level)

    def pack_analog_copies(self):
        if self.pim_mode != "analog":
            return
        max_slots = 3  # 3 outputs at most for AAP
        pack_count = 0
        for i, inst in enumerate(self.instruction_sequence):
            if inst.suspended:
                continue
            if inst.get_opcode() in ["copy", "mv"]:
                if inst.get_src_operands() == inst.get_dest_operands():
                    continue # skip
                target_opcode = ["copy", "mv"]
            elif inst.get_opcode() in ["zero", "one"]:
                target_opcode = [inst.get_opcode()]
            else:
                self.update_source_lines(inst)
                self.new_instruction_sequence.append(inst)
                continue
            # look ahead for packing opportunities
            while len(inst.get_dest_operands()) < max_slots:
                idx_to_pack = self.find_next_packable_instruction(i, target_opcode, inst.get_src_operands())
                if idx_to_pack is not None:
                    inst_to_pack = self.instruction_sequence[idx_to_pack]
                    self.pack_instructions(inst, inst_to_pack)
                    inst_to_pack.suspended = True  # Mark the packed instruction as suspended
                    self.update_line_map(inst_to_pack.line, [inst])
                    pack_count += 1
                    if self.debug_level >= 2:
                        print(f"DEBUG: Packing instruction {idx_to_pack} to instruction at index {i}")
                        print(f"       {idx_to_pack} -> {inst_to_pack}")
                        print(f"       {i} -> {inst}")
                    continue
                else:
                    break
            self.new_instruction_sequence.append(inst)
        print(f"INFO: Summary: Packed {pack_count} analog copy/zero/one instructions.")

    def find_next_packable_instruction(self, idx, op_code, orig_src):
        """ Find the next instruction that can be packed with the current one """
        visited_operands = set()
        window_size = 100
        for i in range(idx + 1, len(self.instruction_sequence)):
            if i - idx > window_size:
                break
            inst = self.instruction_sequence[i]
            srcs = inst.get_src_operands()
            dests = inst.get_dest_operands()
            if inst.get_opcode() in ["copy", "mv"] and srcs == dests:
                inst.suspended = True
                continue
            if inst.get_opcode() in op_code and not inst.suspended:
                packable = (set(srcs) == set(orig_src) and
                            not any(operand in visited_operands for operand in srcs + dests))
                if packable:
                    return i
            srcs = inst.get_src_operands()
            dests = inst.get_dest_operands()
            visited_operands.update(srcs)
            visited_operands.update(dests)
        return None

    def pack_instructions(self, inst, inst_to_pack):
        """ Pack two instructions together """
        srcs = inst.get_src_operands()
        dests = inst.get_dest_operands() + inst_to_pack.get_dest_operands()
        inst.operandsList = dests + srcs

