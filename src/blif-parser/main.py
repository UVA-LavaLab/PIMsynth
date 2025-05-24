#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: main.py
Description: BLIF parser and C generator
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu> - BLIF-to-C parser generator code framework
Date: 2024-09-03
"""

import sys
import argparse
import os
from parser import *
from generator import *
from generator_asm import *
from generator_bitwise import *
from fanout_normalizer import *
from input_copy_inserter import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util import *

if __name__ == "__main__":
    # Set up argument parser with optional arguments
    parser = argparse.ArgumentParser(description='Parse circuit representation and generate C++ code.')
    parser.add_argument('--input-file', '-i', type=str, required=True, help='The input circuit representation file to parse.')
    parser.add_argument('--output-file', '-o', type=str, required=True, help='The output C++ file.')
    parser.add_argument('--module-name', '-m', type=str, required=True, help='The name of the module to parse.')
    parser.add_argument('--output-format', '-f', type=str, required=True, choices=['asm', 'bitwise', 'cpp'], help='Output format: asm, bitwise, or cpp.')
    parser.add_argument('--num-regs', '-r', type=int, default=4, choices=range(2, 20), help='Number of registers 2~16')
    parser.add_argument('--pim-mode', '-p', type=str, default='digital', help='The PIM architecture mode (analog/digital).')

    # Parse the arguments
    args = parser.parse_args()

    # Read the file content
    fileContent = getContent(args.input_file)

    # Parser ctor
    parser = Parser(moduleName=args.module_name)

    # Parse the circuit representation
    parser.parse(fileContent)

    # Transform the DAG
    if args.pim_mode == "analog":
        print("Info: Generate code for analog PIM.")
        inputCopyInserter = InputCopyInserter()
        parser.dag = inputCopyInserter.apply(parser.dag)
        parser.wireList.extend(inputCopyInserter.newWires)

        fanoutNormalizer = FanoutNormalizer()
        parser.dag = fanoutNormalizer.apply(parser.dag)
        parser.wireList.extend(fanoutNormalizer.newWires)
        parser.gatesList = parser.dag.getTopologicallySortedGates()

    # Print the module
    # print("Info: Module name = ", parser.moduleName)
    # print("Info: Inputs = ", parser.inputsList)
    # print("Info: Outputs = ", parser.outputsList)
    # print("Info: Wires = ", parser.wireList)
    # print("\nInfo: Gates List")
    # for gate in parser.gatesList:
        # print(gate)
    # print()

    # Generate the code
    code = ''
    if args.output_format == 'cpp':
        generator = Generator(parser)
        code = generator.generateCode()
    elif args.output_format == 'asm':
        generator = GeneratorAsm(parser, args.num_regs, args.module_name, args.pim_mode)
        code = generator.generateCode()
    elif args.output_format == 'bitwise':
        generator = GeneratorBitwise(parser, args.num_regs, args.module_name, args.pim_mode)
        code = generator.generateCode()

    # Write the generated C++ code into a file
    writeToFile(args.output_file, code)

