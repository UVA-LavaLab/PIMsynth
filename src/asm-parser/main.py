
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
    parser = argparse.ArgumentParser(description='Parse circuit representation and generate C++ code.')
    parser.add_argument('--input-file', '-i', type=str, required=True, help='The input circuit representation file to parse.')
    parser.add_argument('--output-file', '-o', type=str, required=True, help='The output C++ file.')
    parser.add_argument('--module-name', '-m', type=str, required=True, help='The name of the module to parse.')

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

    # Print the bit-serial assembly
    for statement in bitSerialAsm:
        print(statement)

    # Generate bit-serial code following PIMeval API
    generator = PimEvalAPICodeGenerator(bitSerialAsm, args.module_name, asmTransformer.ports)
    code = generator.generateCode()

    # Print the bit-serial code for debugging
    print(code)

    # Write the generated C++ code into a file
    writeToFile(args.output_file, code)


