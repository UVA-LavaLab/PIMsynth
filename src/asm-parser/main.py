#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: main.py
Description: bit-serial code generator in either assembly or PIMeval API
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu> - RISCV-to-BITSERIAL parser generator code framework
Author: Deyuan Guo <guodeyuan@gmail.com>
Date: 2024-09-27
"""

import sys
import argparse
import os
from parser import *
from asm_translator import *
from stats_generator import *
from digital_pimeval_code_generator import *
from analog_pimeval_code_generator import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util import *

if __name__ == "__main__":
    # Set up argument parser with optional arguments
    parser = argparse.ArgumentParser(description='Parse RISV assembly and generate either bit-serial assembly or PIMeval API function.')
    parser.add_argument('--input-file', '-i', type=str, required=True, help='The input assembly file.')
    parser.add_argument('--output-file', '-o', type=str, required=True, help='The output C++ file.')
    parser.add_argument('--module-name', '-m', type=str, required=True, help='The name of the module to parse.')
    parser.add_argument('--output-format', '-f', type=str, required=True, help='Output format: asm or cpp.')
    parser.add_argument('--pim-mode', '-p', type=str, default='digital', help='The PIM architecture mode (analog/digital).')

    # Parse the arguments
    args = parser.parse_args()

    # Read the file content as lines
    lines = getFileLines(args.input_file)

    # Parser ctor
    parser = Parser(moduleName=args.module_name)

    # Parse the circuit representation
    parser.parse(lines)
    riscvStatementList = parser.statementList
    inputList = list(set(parser.inputList))
    outputList = list(set(parser.outputList))

    debugLevel = 0

    # Transrom the riscv assembly to bit-serial assembly
    asmTranslator = AsmTranslator(riscvStatementList, inputList, outputList, pimMode=args.pim_mode, debugLevel=debugLevel)
    asmTranslator.translate()
    asmTranslator.shrink_temp_variables()
    bitSerialAsm = asmTranslator.getBitSerialAsm()

    statsGenerator = StatsGenerator(bitSerialAsm)
    stats = statsGenerator.generateStats()

    print("Info: ", stats)

    if args.output_format == "asm":
        # Generate bit-serial assembly code
        generator = bitSerialAsmCodeGenerator(bitSerialAsm)
        code = "#" + stats + "\n"
        code += generator.generateCode()
    elif args.output_format == "cpp":
        generatorClassMap = {
            "analog": PimEvalAPIAnalogCodeGenerator,
            "digital": PimEvalAPIDigitalCodeGenerator,
        }
        if args.pim_mode not in generatorClassMap:
            raise ValueError(f"Error: Unsupported PIM mode: {args.pim_mode}")
        generatorClass = generatorClassMap[args.pim_mode]
        codeGenerator = generatorClass(bitSerialAsm, args.module_name, asmTranslator.ports)
        code = f"//{stats}\n" + codeGenerator.generateCode()
    else:
        raise ValueError(f"Error: Unknown output format {args.output_format}")

    # Write the generated ASM/C++ code into a file
    writeToFile(args.output_file, code)

