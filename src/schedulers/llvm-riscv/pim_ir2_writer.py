#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: code_gen_pim_ir2.py
Description: Generator for PIM IR-2 intermediate representation (post-scheduling)
Author: Deyuan Guo <guodeyuan@gmail.com>
Date: 2026-03-30
"""

from riscv_asm_translator import LinkedInstruction
from util import natural_sorted


class CodeGenPimIr2:
    """Generator for PIM IR-2 intermediate representation.

    PIM IR-2 is a text-based, line-oriented, post-scheduling format:

        # PIM IR-2
        .module <module_name>
        .mode <digital|analog>
        .num_regs <N>
        .inputs <input1> <input2> ...
        .outputs <output1> <output2> ...
        .spills <temp0> <temp1> ...

        <opcode> <dest1> [<dest2> ...], <src1>[, <src2>[, <src3>]]
        ...

    Operand convention matches IR-1: outputs before first comma, inputs after.
    For gates with no inputs (zero, one): just the output operand(s).
    Registers use generic names: r0, r1, r2, ...
    """

    def __init__(self, instruction_sequence, module_name, pim_mode, num_regs, input_list, output_list):
        self.instruction_sequence = instruction_sequence
        self.module_name = module_name
        self.pim_mode = pim_mode
        self.num_regs = num_regs
        self.input_list = natural_sorted(input_list)
        self.output_list = natural_sorted(output_list)
        self.reg_map = self._build_reg_map(num_regs)

    def _build_reg_map(self, num_regs):
        """Build mapping from RISC-V register names to generic rN names."""
        all_regs = [f't{i}' for i in range(7)] + [f's{i}' for i in range(12)]
        return {reg: f'r{i}' for i, reg in enumerate(all_regs[:num_regs])}

    def _get_analog_opcode(self, opcode, num_dests):
        """Map bare opcode to analog opcode name, consistent with IR-1.

        Naming rules (same as generator_pim_ir1.py):
        - Digit-ending: append 'a' (inv1 -> inv1a, and2 -> and2a)
        - Letter-ending: append '_a' (copy -> copy_a, zero -> zero_a)
        - maj3: becomes maj3a_o1/_o2/_o3 based on dest count
        - read/write: unchanged (spill ops)
        Handles __nXXX suffix: splits off, renames base, reattaches.
        """
        suffix = ''
        base = opcode
        if '__n' in opcode:
            parts = opcode.split('__n', 1)
            base = parts[0]
            suffix = '__n' + parts[1]

        if base in ('read', 'write'):
            return opcode

        if base == 'maj3':
            if num_dests == 2:
                analog_base = 'maj3a_o2'
            elif num_dests == 3:
                analog_base = 'maj3a_o3'
            else:
                analog_base = 'maj3a_o1'
            return analog_base + suffix

        if base[-1].isdigit():
            return base + 'a' + suffix
        return base + '_a' + suffix

    def _map_operand(self, operand):
        """Map a single operand: RISC-V reg -> rN, others unchanged."""
        if operand in self.reg_map:
            return self.reg_map[operand]
        return operand

    def _get_spill_list(self):
        """Collect spill variable names (tempN) from instruction operands."""
        spills = set()
        for instr in self.instruction_sequence:
            if hasattr(instr, 'suspended') and instr.suspended:
                continue
            for operand in instr.operandsList:
                if operand.startswith('temp'):
                    spills.add(operand)
        return natural_sorted(spills)

    def generate_code(self):
        """Generate PIM IR-2 text."""
        code = self._generate_header()
        code += self._generate_instructions()
        return code

    def _generate_header(self):
        """Generate IR-2 header directives."""
        code = "# PIM IR-2\n"
        code += f".module {self.module_name}\n"
        code += f".mode {self.pim_mode}\n"
        code += f".num_regs {self.num_regs}\n"
        code += f".inputs {' '.join(self.input_list)}\n"
        code += f".outputs {' '.join(self.output_list)}\n"
        spills = self._get_spill_list()
        if spills:
            code += f".spills {' '.join(spills)}\n"
        else:
            code += ".spills\n"
        code += "\n"
        return code

    def _generate_instruction(self, instr):
        """Generate a single IR-2 instruction line."""
        opcode = instr.opCode
        operands = instr.operandsList

        dests = LinkedInstruction.get_dest_operands_from_opcode(opcode, operands)
        srcs = LinkedInstruction.get_src_operands_from_opcode(opcode, operands)

        if self.pim_mode == 'analog':
            opcode = self._get_analog_opcode(opcode, len(dests))

        mapped_dests = [self._map_operand(d) for d in dests]
        mapped_srcs = [self._map_operand(s) for s in srcs]

        if not mapped_srcs:
            return f"{opcode} {' '.join(mapped_dests)}\n"
        dest_str = ' '.join(mapped_dests)
        src_str = ', '.join(mapped_srcs)
        return f"{opcode} {dest_str}, {src_str}\n"

    def _generate_instructions(self):
        """Generate all IR-2 instruction lines."""
        code = ""
        for instr in self.instruction_sequence:
            if hasattr(instr, 'suspended') and instr.suspended:
                continue
            code += self._generate_instruction(instr)
        return code
