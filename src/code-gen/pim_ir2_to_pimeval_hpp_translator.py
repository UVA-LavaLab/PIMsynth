#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: pim_ir2_to_pimeval_hpp_translator.py
Description: Translate PIM IR-2 file to PIMeval microprogram hpp.
Author: Deyuan Guo <guodeyuan@gmail.com>
Date: 2026-04-01
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))

from pim_ir2_reader import read_pim_ir2
from stats_generator import StatsGenerator
from code_gen_pimeval_digital import PimEvalAPIDigitalCodeGenerator
from code_gen_pimeval_analog import PimEvalAPIAnalogCodeGenerator
from util import writeToFile


class _Instruction:
    """Lightweight instruction object satisfying the interface expected by
    code_gen_pimeval_* and StatsGenerator (opCode, operandsList, line,
    isReadInstruction, isWriteInstruction).
    """

    def __init__(self, opCode, operandsList, line):
        self.opCode = opCode
        self.operandsList = operandsList
        self.line = line

    def isReadInstruction(self):
        return self.opCode == 'read'

    def isWriteInstruction(self):
        return self.opCode == 'write'


def _reverse_analog_opcode(opcode):
    """Reverse analog opcode naming to recover bare opcode for code-gen.

    Analog IR-2 opcodes carry a/a_ suffix (inv1a -> inv1, copy_a -> copy,
    maj3a_o1 -> maj3). This is a PIM-level naming convention, not RISC-V
    specific.
    """
    suffix = ''
    base = opcode
    if '__n' in opcode:
        parts = opcode.split('__n', 1)
        base = parts[0]
        suffix = '__n' + parts[1]

    if base in ('read', 'write'):
        return opcode

    if base.startswith('maj3a'):
        return 'maj3' + suffix

    if base.endswith('_a'):
        return base[:-2] + suffix

    if base.endswith('a') and len(base) > 1 and base[-2].isdigit():
        return base[:-1] + suffix

    return opcode


def _build_instruction_sequence(ir2_data):
    """Convert parsed PimIr2Data instructions into _Instruction objects
    with the operandsList ordering expected by code_gen_pimeval_* classes.
    """
    sequence = []
    for idx, (opcode, dests, srcs) in enumerate(ir2_data.instructions):
        if ir2_data.mode == 'analog':
            bare_opcode = _reverse_analog_opcode(opcode)
        else:
            bare_opcode = opcode

        # Reconstruct operandsList in the order code_gen_pimeval expects:
        #   write: [src_reg, dest_port]
        #   all others: dests + srcs
        if bare_opcode == 'write':
            operands_list = srcs + dests
        else:
            operands_list = dests + srcs

        instr = _Instruction(bare_opcode, operands_list, idx + 1)
        sequence.append(instr)
    return sequence


def translate_ir2_to_hpp(ir2_file, hpp_file):
    """Read a PIM IR-2 file and generate a PIMeval microprogram hpp file."""
    ir2_data = read_pim_ir2(ir2_file)
    instruction_sequence = _build_instruction_sequence(ir2_data)

    stats = StatsGenerator(instruction_sequence).generateStats()
    print("Info: ", stats)

    ports = set(ir2_data.inputs + ir2_data.outputs)
    generator_map = {
        'digital': PimEvalAPIDigitalCodeGenerator,
        'analog': PimEvalAPIAnalogCodeGenerator,
    }
    if ir2_data.mode not in generator_map:
        raise ValueError(f"Unsupported PIM mode: {ir2_data.mode}")

    gen_class = generator_map[ir2_data.mode]
    code_gen = gen_class(instruction_sequence, ir2_data.module_name, ports)
    code = f"//{stats}\n" + code_gen.generateCode()
    writeToFile(hpp_file, code)
