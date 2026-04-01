#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: generator_pim_ir1.py
Description: Generator for PIM IR-1 intermediate representation
Author: Deyuan Guo <guodeyuan@gmail.com>
Date: 2026-02-12
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'utils'))
from util import natural_sorted


class GeneratorPimIr1():
    """ Generator for PIM IR-1 intermediate representation

    PIM IR-1 is a text-based, line-oriented format:

        # PIM IR-1
        .module <module_name>
        .mode <digital|analog>
        .num_regs <N>
        .inputs <input1> <input2> ...
        .outputs <output1> <output2> ...
        .temps <temp1> <temp2> ...

        <opcode>[__n<inv_bits>] <dest>, <src1>[, <src2>[, <src3>]]
        ...

    Operand convention: outputs before first comma, inputs after.
    For gates with no inputs (zero, one): just the output operand.
    For multi-output gates: outputs are space-separated before the first comma.
    """

    def __init__(self, dag, pim_mode, num_regs):
        """ Init """
        self.dag = dag
        self.pim_mode = pim_mode
        self.num_regs = num_regs

    def sanitize_token_list(self, token_list):
        """ Sanitize token names """
        return [self.dag.sanitize_name(token) for token in token_list]

    def generate_code(self):
        """ Generate PIM IR-1 text """
        code = self.generate_header()
        code += self.generate_instructions()
        return code

    def generate_header(self):
        """ Generate IR-1 header directives """
        code = "# PIM IR-1\n"
        code += f".module {self.dag.module_name}\n"
        code += f".mode {self.pim_mode}\n"
        code += f".num_regs {self.num_regs}\n"
        inputs = natural_sorted(self.sanitize_token_list(self.dag.get_in_ports()))
        outputs = natural_sorted(self.sanitize_token_list(self.dag.get_out_ports()))
        code += f".inputs {' '.join(inputs)}\n"
        code += f".outputs {' '.join(outputs)}\n"
        temps = natural_sorted(self.sanitize_token_list(self.dag.get_wire_name_list()))
        code += f".temps {' '.join(temps)}\n"
        code += "\n"
        return code

    def get_analog_opcode(self, gate_func, num_outputs):
        """ Map generic gate_func to analog opcode name.
        Naming rule: append 'a' if name ends with digit, '_a' if letter.
        For maj3, append _o2 or _o3 for multi-output variants.
        """
        if gate_func == 'maj3':
            base = 'maj3a_o1'
            if num_outputs == 2:
                return 'maj3a_o2'
            elif num_outputs == 3:
                return 'maj3a_o3'
            return base
        if gate_func[-1].isdigit():
            return gate_func + 'a'
        return gate_func + '_a'

    def get_gate_func_encoding(self, gate_id):
        """ Get gate function name with optional inversion suffix.
        In analog mode, maps generic names to mode-specific opcodes.
        """
        gate = self.dag.graph.nodes[gate_id]
        gate_func = gate['gate_func']

        if self.pim_mode == 'analog':
            encoding = self.get_analog_opcode(gate_func, len(gate['outputs']))
        else:
            encoding = gate_func

        inv_str = ''
        for i, _ in enumerate(gate['inputs']):
            is_inv = gate['inputs'][i] in gate['inverted']
            inv_str += '1' if is_inv else '0'
        if '1' in inv_str:
            encoding += f"__n{inv_str}"
        return encoding

    def generate_instruction(self, gate_id):
        """ Generate a single IR-1 instruction line """
        gate = self.dag.graph.nodes[gate_id]
        gate_func = gate['gate_func']
        if gate_func in ['in_port', 'out_port']:
            return ""

        opcode = self.get_gate_func_encoding(gate_id)
        outputs = self.sanitize_token_list(gate['outputs'])
        inputs = self.sanitize_token_list(gate['inputs'])

        if len(inputs) == 0:
            return f"{opcode} {' '.join(outputs)}\n"
        dest_str = ' '.join(outputs)
        src_str = ', '.join(inputs)
        return f"{opcode} {dest_str}, {src_str}\n"

    def generate_instructions(self):
        """ Generate all IR-1 instruction lines in topological order """
        code = ""
        for gate_id in self.dag.get_topo_sorted_gate_id_list():
            code += self.generate_instruction(gate_id)
        return code
