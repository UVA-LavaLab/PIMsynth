
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
    parser.add_argument('--asm', action='store_true', help='Generates bit-serial assembly code if set')

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

    if args.asm:
        # Generate bit-serial assembly code
        generator = bitSerialAsmCodeGenerator(bitSerialAsm)
        code = generator.generateCode()
    else:
        # Generate bit-serial code following PIMeval API
        generator = PimEvalAPICodeGenerator(bitSerialAsm, args.module_name, asmTransformer.ports)
        code = generator.generateCode()

    # Write the generated C++ code into a file
    writeToFile(args.output_file, code)


