#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: main.py
Description: Bit-serial compiler BLIF translator
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Author: Deyuan Guo <guodeyuan@gmail.com>
Date: 2024-09-03
"""

import sys
import argparse
import os
import traceback
import networkx as nx

import blif_parser
from blif_dag import DAG

from dag_transformer_base import DagTransformer
from dag_input_port_isolation import InputPortIsolation
from dag_maj_normalizer import MajNormalizer
from dag_inv_eliminator import InvEliminator
from dag_inout_var_reusing import InoutVarReusing
from dag_multi_dest_optimizer import MultiDestOptimizer
from dag_wire_copy_inserter import WireCopyInserter

from generator_asm import GeneratorAsm
from generator_bitwise import GeneratorBitwise

# TODO: avoid importing util from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import util


class BlifTranslator:
    """ Bit-serial compiler BLIF translator class """

    def __init__(self):
        """ Initialize the BLIF translator """
        self.input_file = ''
        self.module_name = ''
        self.output_file_prefix = ''
        self.output_formats = ''
        self.num_regs = 0
        self.pim_mode = ''
        self.visualize = False
        self.debug_level = 0


    def parse_args(self, input_args):
        """ Parse command line arguments """
        arg_parser = argparse.ArgumentParser(description='BLIF Translator')
        arg_parser.add_argument('--input-file', '-i', type=str, required=True, help='Input circuit in BLIF format')
        arg_parser.add_argument('--module-name', '-m', type=str, required=True, help='Bit-serial compiler module name')
        arg_parser.add_argument('--output-file-prefix', '-o', type=str, required=True, help='Bit-serial compiler output file name prefix')
        arg_parser.add_argument('--output-formats', '-f', type=str, required=True, help='Output formats: comma-separated: asm and/or bitwise')
        arg_parser.add_argument('--num-regs', '-r', type=int, default=4, choices=range(2, 16), help='Number of registers 2~16')
        arg_parser.add_argument('--pim-mode', '-p', type=str, default='digital', choices=['digital', 'analog'], help='PIM architecture mode: digital, analog')
        arg_parser.add_argument('--visualize', action='store_true', default=False, help='Enable visualization of the DAG')
        arg_parser.add_argument('--debug_level', type=int, default=1, help='Enable debug messages')

        args = arg_parser.parse_args(input_args)

        self.input_file = args.input_file
        self.module_name = args.module_name
        self.output_file_prefix = args.output_file_prefix
        self.output_formats = args.output_formats
        self.num_regs = args.num_regs
        self.pim_mode = args.pim_mode
        self.visualize = args.visualize
        self.debug_level = args.debug_level

        if self.debug_level >= 2 and 'asm' in self.output_formats:
            self.visualize = True

        success = True
        if not os.path.isfile(self.input_file):
            print(f"Error: Input file '{self.input_file}' does not exist.")
            success = False

        if not success:
            raise ValueError("Invalid command line arguments")

    def debug_checkpoint(self, dag, tag):
        """ Print or visualizer the DAG for debugging """
        if self.debug_level >= 1:
            print("Info: BLIF translator DAG checkpoint", tag)

        if self.visualize:
            DAG.save_dag_as_json(dag, f"dag_{tag}.json")
            DAG.draw_interactive_circuit(dag, f"G_{tag}.html")

        if self.debug_level >= 2:
            print(f"DEBUG: DAG {tag} - Module Name = {dag.module_name}")
            enable_breakpoint = self.debug_level >= 3
            dag.debug_print(enable_breakpoint)


    def run_digital_optimization(self, dag):
        """ Run optimizations for digital PIM mode """
        print("Info: Optimizing DAG for digital PIM")

        # Digital PIM: Normalize majority gates
        #maj_normalizer = MajNormalizer()
        #maj_normalizer.apply(dag)
        #self.debug_checkpoint(dag, "post_maj_norm")


    def run_analog_optimization(self, dag):
        """ Run optimizations for analog PIM mode """
        print("Info: Optimizing DAG for analog PIM")

        # Analog PIM: Copy external inputs to register rows
        input_port_isolation = InputPortIsolation()
        input_port_isolation.apply(dag)
        self.debug_checkpoint(dag, "post_input_port_iso")

        # Analog PIM: Normalize majority gates
        maj_normalizer = MajNormalizer()
        maj_normalizer.apply(dag)
        self.debug_checkpoint(dag, "post_maj_norm")

        # Analog PIM: Eliminate inverters
        #inv_eliminator = InvEliminator()
        #inv_eliminator.apply(dag)
        #self.debug_checkpoint(dag, "post_inv_elim")

        ## Analog PIM: Reuse TRA inputs to drive next stage gates
        inout_var_reuse = InoutVarReusing()
        inout_var_reuse.apply(dag)
        self.debug_checkpoint(dag, "post_inout_var_reuse")

        ## Analog PIM: Utilize multi-destination gates
        #multi_dest_optimizer = MultiDestOptimizer(self.num_regs)
        #multi_dest_optimizer.apply(dag)
        #self.debug_checkpoint(dag, "post_multi_dest_opt")

        ## Analog PIM: Copy wires that drives multiple input-destroying gates
        wire_copy_inserter = WireCopyInserter()
        wire_copy_inserter.apply(dag)
        self.debug_checkpoint(dag, "post_wire_copy")


    def run_code_generation(self, dag):
        """ Run code generation based on the output format """
        code = ''
        if 'asm' in self.output_formats:
            print("Info: Generating inline assembly IR for PIM")
            # TODO: use self.module_name instead of func here
            generator = GeneratorAsm(dag, self.num_regs, 'func', self.pim_mode)
            code = generator.generate_code()
            out_file = self.output_file_prefix + '.c'
            if os.path.isfile(out_file):
                print(f"Warning: Output file '{out_file}' already exists and will be overwritten.")
            util.writeToFile(out_file, code)
        if 'bitwise' in self.output_formats:
            print("Info: Generating bitwise IR for PIM")
            generator = GeneratorBitwise(dag, self.num_regs, self.module_name, self.pim_mode)
            code = generator.generate_code()
            out_file = self.output_file_prefix + '.bitwise.c'
            if os.path.isfile(out_file):
                print(f"Warning: Output file '{out_file}' already exists and will be overwritten.")
            util.writeToFile(out_file, code)


    def run(self, input_args):
        """ Run the BLIF parser """
        self.parse_args(input_args)
        DagTransformer.debug_level = self.debug_level

        # Run BLIF parser
        parser = blif_parser.BlifParser(self.module_name)
        file_content = util.getContent(self.input_file)
        parser.parse(file_content)
        in_ports = parser.get_in_ports()
        out_ports = parser.get_out_ports()
        gate_info_list = parser.get_gate_info_list()

        # Create the DAG
        dag = DAG(
            module_name=self.module_name,
            in_ports=in_ports,
            out_ports=out_ports,
            gate_info_list=gate_info_list,
            debug_level=self.debug_level
        )

        self.debug_checkpoint(dag, "initial")

        # Run ananlog optimizations if needed
        if self.pim_mode == "analog":
            self.run_analog_optimization(dag)
        elif self.pim_mode == "digital":
            self.run_digital_optimization(dag)

        self.debug_checkpoint(dag, "final")

        # Generate code into the output file
        self.run_code_generation(dag)


# Main entry point
if __name__ == "__main__":
    blif_translator = BlifTranslator()
    try:
        blif_translator.run(sys.argv[1:])
        print("Info: BLIF translation completed successfully.")
        sys.exit(0)
    except Exception as e:
        traceback.print_exc()
        print(f"Error: BLIF translation failed: {e}")
        sys.exit(1)

