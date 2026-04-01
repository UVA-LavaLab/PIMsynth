#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: pim_target.py
Description: Minimal PIM target machine description for scheduling
Author: Deyuan Guo <dg7vp@virginia.edu>
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Author: Matthew Hoffmann <mrh259@cornell.edu>
"""

# Costs are in DRAM cycles; a typical cycle is tCK = 0.63ns
TIMING = {
    'tCCD': 4,
    'tRC': 74,
}

OPCODES = {
    # -- Digital compute ops (latency: tCCD) --
    'inv1':  { 'latency': 'tCCD', 'operands': ['reg_out', 'reg_in'] },
    'and2':  { 'latency': 'tCCD', 'operands': ['reg_out', 'reg_in', 'reg_in'] },
    'nand2': { 'latency': 'tCCD', 'operands': ['reg_out', 'reg_in', 'reg_in'] },
    'or2':   { 'latency': 'tCCD', 'operands': ['reg_out', 'reg_in', 'reg_in'] },
    'nor2':  { 'latency': 'tCCD', 'operands': ['reg_out', 'reg_in', 'reg_in'] },
    'xor2':  { 'latency': 'tCCD', 'operands': ['reg_out', 'reg_in', 'reg_in'] },
    'xnor2': { 'latency': 'tCCD', 'operands': ['reg_out', 'reg_in', 'reg_in'] },
    'mux2':  { 'latency': 'tCCD', 'operands': ['reg_out', 'reg_in', 'reg_in', 'reg_in'] },
    'maj3':  { 'latency': 'tCCD', 'operands': ['reg_out', 'reg_in', 'reg_in', 'reg_in'] },
    'zero':  { 'latency': 'tCCD', 'operands': ['reg_out'] },
    'one':   { 'latency': 'tCCD', 'operands': ['reg_out'] },
    'mv':    { 'latency': 'tCCD', 'operands': ['reg_out', 'reg_in'] },

    # -- Digital spill ops (latency: tRC) --
    'read':  { 'latency': 'tRC', 'operands': ['reg_out', 'row_in'] },
    'write': { 'latency': 'tRC', 'operands': ['row_out', 'reg_in'] },

    # -- Analog compute ops (latency: tRC) --
    # Opcodes in IR-1 may have an additional __n### suffix (e.g. maj3a_o1__n010)
    # denoting DCC-based input negation. Strip the suffix to look up the base opcode.
    'inv1a':        { 'latency': 'tRC', 'operands': ['row_out', 'row_in'] },
    'and2a':        { 'latency': 'tRC', 'operands': ['row_out', 'row_inout', 'row_inout'] },
    'or2a':         { 'latency': 'tRC', 'operands': ['row_out', 'row_inout', 'row_inout'] },
    'maj3a_o1':     { 'latency': 'tRC', 'operands': ['row_out', 'row_inout', 'row_inout', 'row_inout'] },
    'maj3a_o2':     { 'latency': 'tRC', 'operands': ['row_out', 'row_out', 'row_inout', 'row_inout', 'row_inout'] },
    'maj3a_o3':     { 'latency': 'tRC', 'operands': ['row_out', 'row_out', 'row_out', 'row_inout', 'row_inout', 'row_inout'] },
    'copy_a':       { 'latency': 'tRC', 'operands': ['row_out', 'row_in'] },
    'copy_inout_a': { 'latency': 'tRC', 'operands': ['row_out', 'row_inout'] },
    'zero_a':       { 'latency': 'tRC', 'operands': ['row_out'] },
    'one_a':        { 'latency': 'tRC', 'operands': ['row_out'] },
}
