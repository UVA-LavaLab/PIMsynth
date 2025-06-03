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

import blif_parser
import blif_dag
from dag_maj_normalizer import MajNormalizer
from dag_input_copy_inserter import InputCopyInserter
from dag_fanout_normalizer import FanoutNormalizer
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
        self.output_file = ''
        self.module_name = ''
        self.output_format = ''
        self.num_regs = 0
        self.pim_mode = ''
        self.visualize = False
        self.debug = False


    def parse_args(self, input_args):
        """ Parse command line arguments """
        arg_parser = argparse.ArgumentParser(description='BLIF Translator')
        arg_parser.add_argument('--input-file', '-i', type=str, required=True, help='Input circuit in BLIF format')
        arg_parser.add_argument('--output-file', '-o', type=str, required=True, help='Bit-serial compiler output file')
        arg_parser.add_argument('--module-name', '-m', type=str, required=True, help='Bit-serial compiler module name')
        arg_parser.add_argument('--output-format', '-f', type=str, required=True, choices=['asm', 'bitwise'], help='Output format: asm, bitwise')
        arg_parser.add_argument('--num-regs', '-r', type=int, default=4, choices=range(2, 16), help='Number of registers 2~16')
        arg_parser.add_argument('--pim-mode', '-p', type=str, default='digital', choices=['digital', 'analog'], help='PIM architecture mode: digital, analog')
        arg_parser.add_argument('--visualize', action='store_true', default=False, help='Enable visualization of the DAG')
        arg_parser.add_argument('--debug', action='store_true', default=False, help='Enable debug mode')

        args = arg_parser.parse_args(input_args)

        self.input_file = args.input_file
        self.output_file = args.output_file
        self.module_name = args.module_name
        self.output_format = args.output_format
        self.num_regs = args.num_regs
        self.pim_mode = args.pim_mode
        self.visualize = args.visualize
        self.debug = args.debug

        success = True
        if not os.path.isfile(self.input_file):
            print(f"Error: Input file '{self.input_file}' does not exist.")
            success = False
        if os.path.isfile(self.output_file):
            print(f"Warning: Output file '{self.output_file}' already exists and will be overwritten.")

        if not success:
            raise ValueError("Invalid command line arguments")


    def run_analog_optimization(self, dag):
        """ Run optimizations for analog PIM mode """
        print("Info: Optimizing DAG for analog PIM")
        if self.visualize:
            util.save_dag_as_json(dag, "dag_pre_pass.json")

        # Analog PIM: Normalize majority gates
        #maj_normalizer = MajNormalizer()
        #maj_normalizer.apply(dag)

        # Analog PIM: Copy external inputs to register rows
        input_copy_inserter = InputCopyInserter()
        input_copy_inserter.apply(dag)

        # Analog PIM: Replicate gate inputs due to input-destroying TRA
        fanout_normalizer = FanoutNormalizer()
        fanout_normalizer.apply(dag)

        if self.visualize:
            blif_dag.save_dag_as_json(dag, "dag_post_pass.json")

        if self.debug:
            print("DEBUG: Module Name = ", self.module_name)
            print("DEBUG: Input Ports = ", dag.inPortList)
            print("DEBUG: Output Ports = ", dag.outPortList)
            print("DEBUG: Wires = ", dag.wireList)
            print(dag)
            breakpoint()

        if self.visualize:
            dag_pre_pass = blif_dag.load_dag_from_json("dag_pre_pass.json")
            dag_post_pass = blif_dag.load_dag_from_json("dag_post_pass.json")
            blif_dag.draw_interactive_circuit(dag_pre_pass, "G_pre_pass.html")
            blif_dag.draw_interactive_circuit(dag_post_pass, "G_post_pass.html")

        # Temp: Remove trailing stars from gates list
        fanout_normalizer.remove_trailing_stars_from_gate_list(dag)


    def run_code_generation(self, dag):
        """ Run code generation based on the output format """
        code = ''
        if self.output_format == 'asm':
            print("Info: Generating inline assembly IR for PIM")
            generator = GeneratorAsm(dag, self.num_regs, self.module_name, self.pim_mode)
            code = generator.generate_code()
        elif self.output_format == 'bitwise':
            print("Info: Generating bitwise IR for PIM")
            generator = GeneratorBitwise(dag, self.num_regs, self.module_name, self.pim_mode)
            code = generator.generate_code()
        else:
            raise ValueError(f"Error: Unknown output format '{self.output_format}'")

        # Write the generated C++ code into a file
        util.writeToFile(self.output_file, code)


    def run(self, input_args):
        """ Run the BLIF parser """
        self.parse_args(input_args)

        # Run BLIF parser
        parser = blif_parser.BlifParser(self.module_name)
        file_content = util.getContent(self.input_file)
        dag = parser.parse(file_content)

        # Run ananlog optimizations if needed
        if self.pim_mode == "analog":
            self.run_analog_optimization(dag)

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

