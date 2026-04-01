#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: pim_ir2_reader.py
Description: Parser for PIM IR-2 intermediate representation files.
Author: Deyuan Guo <dg7vp@virginia.edu>
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Author: Matthew Hoffmann <mrh259@cornell.edu>

PIM IR-2 format (post-scheduling):

    # PIM IR-2
    .module <name>
    .mode <digital|analog>
    .num_regs <N>
    .inputs <...>
    .outputs <...>
    .spills <...>

    <opcode>[__n<inv>] <dest1> [<dest2>...], <src1>[, <src2>...]
"""


class PimIr2Data:
    """Structured representation of a parsed .pim_ir2 file."""

    def __init__(self):
        self.module_name = ''
        self.mode = ''
        self.num_regs = 0
        self.inputs = []
        self.outputs = []
        self.spills = []
        self.instructions = []  # list of (opcode, dests_list, srcs_list)


def _parse_instruction(line):
    """Parse a single IR-2 instruction line.

    Format:
        opcode dest1 [dest2 ...], src1[, src2[, ...]]
        opcode dest1               (no comma when there are no inputs)

    Returns (opcode, dests_list, srcs_list).
    """
    parts = line.split(None, 1)
    opcode = parts[0]
    rest = parts[1] if len(parts) > 1 else ''

    if ',' in rest:
        before_comma, after_comma = rest.split(',', 1)
        dests = before_comma.split()
        srcs = [s.strip() for s in after_comma.split(',')]
    else:
        dests = rest.split() if rest else []
        srcs = []

    return opcode, dests, srcs


def read_pim_ir2(filepath):
    """Read a .pim_ir2 file and return a PimIr2Data object."""
    data = PimIr2Data()
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
            elif line.startswith('.spills '):
                data.spills = line.split()[1:]
            elif line.startswith('.'):
                pass  # skip unknown directives
            else:
                inst = _parse_instruction(line)
                data.instructions.append(inst)
    return data
