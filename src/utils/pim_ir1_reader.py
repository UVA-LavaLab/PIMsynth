#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: pim_ir1_reader.py
Description: Parser for PIM IR-1 intermediate representation files.
Author: Deyuan Guo <guodeyuan@gmail.com>
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Author: Matthew Hoffmann <mrh259@cornell.edu>

PIM IR-1 format:

    # PIM IR-1
    .module <name>
    .mode <digital|analog>
    .num_regs <N>
    .inputs <...>
    .outputs <...>
    .temps <...>

    <opcode>[__n<inv>] <dest1> [<dest2>...], <src1>[, <src2>...]
"""


class PimIr1Data:
    """Structured representation of a parsed .pim_ir1 file."""

    def __init__(self):
        self.module_name = ''
        self.mode = ''
        self.num_regs = 0
        self.inputs = []
        self.outputs = []
        self.temps = []
        self.instructions = []  # list of (opcode, outputs_list, inputs_list)


def _parse_instruction(line):
    """Parse a single IR-1 instruction line.

    Format:
        opcode dest1 [dest2 ...], src1[, src2[, ...]]
        opcode dest1               (no comma when there are no inputs)

    Returns (opcode, outputs_list, inputs_list).
    """
    parts = line.split(None, 1)
    opcode = parts[0]
    rest = parts[1] if len(parts) > 1 else ''

    if ',' in rest:
        before_comma, after_comma = rest.split(',', 1)
        outputs = before_comma.split()
        inputs = [s.strip() for s in after_comma.split(',')]
    else:
        outputs = rest.split() if rest else []
        inputs = []

    return opcode, outputs, inputs


def read_pim_ir1(filepath):
    """Read a .pim_ir1 file and return a PimIr1Data object."""
    data = PimIr1Data()
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('.module '):
                data.module_name = line.split(None, 1)[1]
            elif line.startswith('.mode '):
                data.mode = line.split(None, 1)[1]
            elif line.startswith('.num_regs '):
                data.num_regs = int(line.split(None, 1)[1])
            elif line.startswith('.inputs '):
                data.inputs = line.split()[1:]
            elif line.startswith('.outputs '):
                data.outputs = line.split()[1:]
            elif line.startswith('.temps '):
                data.temps = line.split()[1:]
            elif line.startswith('.'):
                pass  # skip unknown directives
            else:
                inst = _parse_instruction(line)
                data.instructions.append(inst)
    return data
