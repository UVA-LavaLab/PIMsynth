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

import blif_parser
import blif_dag
import generator_asm
import generator_bitwise
import fanout_normalizer
import input_copy_inserter
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import util

class BlifTranslator:
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

        self.parser = None


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
            print("Error: Invalid command line arguments.")
        return success


    def run_analog_optimization(self, dag):
        """ Run optimizations for analog PIM mode """
        print("Info: Optimizing DAG for analog PIM")
        if self.visualize:
            util.saveDagAsJson(dag, "dag_pre_pass.json")

        # Analog PIM: Copy external inputs to register rows
        inputCopyInserter = input_copy_inserter.InputCopyInserter()
        dag = inputCopyInserter.apply(dag)
        dag.wireList.extend(inputCopyInserter.newWires)

        # Analog PIM: Replicate gate inputs due to input-destroying TRA
        fanoutNormalizer = fanout_normalizer.FanoutNormalizer()
        dag = fanoutNormalizer.apply(dag)
        dag.wireList.extend(fanoutNormalizer.newWires)

        if self.visualize:
            blif_dag.saveDagAsJson(dag, "dag_post_pass.json")

        if self.debug:
            print("DEBUG: Module name = ", self.module_name)
            print("DEBUG: Inputs = ", self.parser.inputsList)
            print("DEBUG: Outputs = ", self.parser.outputsList)
            print("DEBUG: Wires = ", self.parser.wireList)
            print(dag)
            breakpoint()

        # Temp: Update the gate list in DAG object
        dag.gateList = dag.getTopologicallySortedGates()

        if self.visualize:
            G_pre_pass = blif_dag.loadDagFromJson("dag_pre_pass.json")
            G_post_pass = blif_dag.loadDagFromJson("dag_post_pass.json")
            blif_dag.drawInteractiveCircuit(G_pre_pass, "G_pre_pass.html")
            blif_dag.drawInteractiveCircuit(G_post_pass, "G_post_pass.html")

        # Temp: Remove trailing stars from gates list
        dag.gateList = fanout_normalizer.removeTrailingStarsFromGatesList(dag.gateList)
        return True


    def run_code_generation(self, dag):
        """ Run code generation based on the output format """
        code = ''
        if self.output_format == 'asm':
            print("Info: Generating inline assembly IR for PIM")
            generator = generator_asm.GeneratorAsm(dag, self.num_regs, self.module_name, self.pim_mode)
            code = generator.generateCode()
        elif self.output_format == 'bitwise':
            print("Info: Generating bitwise IR for PIM")
            generator = generator_bitwise.GeneratorBitwise(dag, self.num_regs, self.module_name, self.pim_mode)
            code = generator.generateCode()

        # Write the generated C++ code into a file
        util.writeToFile(self.output_file, code)
        return True


    def run(self, input_args):
        """ Run the BLIF parser """
        success = self.parse_args(input_args)
        if not success:
            return False

        # Run BLIF parser
        self.parser = blif_parser.BlifParser(self.module_name)
        if success:
            fileContent = util.getContent(self.input_file)
            success, dag = self.parser.parse(fileContent)

        # Run ananlog optimizations if needed
        if success and self.pim_mode == "analog":
            success = self.run_analog_optimization(dag)

        # Generate code into the output file
        if success:
            success = self.run_code_generation(dag)

        return success


# Main entry point
if __name__ == "__main__":
    blif_translator = BlifTranslator()
    success = blif_translator.run(sys.argv[1:])
    if not success:
        print("Error: BLIF translation failed.")
        sys.exit(1)
    else:
        print("Info: BLIF translation completed successfully.")
        sys.exit(0)

