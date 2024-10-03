#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: main.py
Description: bit-serial code generator in either assembly or PIMeval API
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu> - RISCV-to-BITSERIAL parser generator code framework
Date: 2024-09-27
"""

import sys
import argparse
import os
from parser import *
from asm_transformer import *
from generator import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util import *

if __name__ == "__main__":
    # Set up argument parser with optional arguments
    parser = argparse.ArgumentParser(description='Parse RISV assembly and generate either bit-serial assembly or PIMeval API function.')
    parser.add_argument('--input-file', '-i', type=str, required=True, help='The input assembly file.')
    parser.add_argument('--output-file', '-o', type=str, required=True, help='The output C++ file.')
    parser.add_argument('--module-name', '-m', type=str, required=True, help='The name of the module to parse.')
    parser.add_argument('--output-format', '-f', type=str, required=True, help='Output format: asm or cpp.')

    # Parse the arguments
    args = parser.parse_args()

    # Read the file content as lines
    lines = getFileLines(args.input_file)

    # Parser ctor
    parser = Parser(moduleName=args.module_name)

    # Parse the circuit representation
    parser.parse(lines)
    riscvStatementList = parser.statementList

    # Transrom the riscv assembly to bit-serial assembly
    asmTransformer = AsmTransformer(riscvStatementList)
    bitSerialAsm = asmTransformer.getBitSerialAsm()

    statsGenerator = StatsGenerator(bitSerialAsm)
    stats = statsGenerator.generateStats()

    print("Info: ", stats)

    if args.output_format == "asm":
        # Generate bit-serial assembly code
        generator = bitSerialAsmCodeGenerator(bitSerialAsm)
        code = "#" + stats + "\n"
        code += generator.generateCode()
    elif args.output_format == "cpp":
        # Generate bit-serial code following PIMeval API
        generator = PimEvalAPICodeGenerator(bitSerialAsm, args.module_name, asmTransformer.ports)
        code = "//" + stats + "\n"
        code += generator.generateCode()
    else:
        print("Error: Unknown output format.")
        exit()

    # Write the generated ASM/C++ code into a file
    writeToFile(args.output_file, code)

