import sys
import argparse
from util import *
from parser import *
from generator import *
from generatorAsm import *

if __name__ == "__main__":
    # Set up argument parser with optional arguments
    parser = argparse.ArgumentParser(description='Parse circuit representation and generate C++ code.')
    parser.add_argument('--input-file', '-i', type=str, required=True, help='The input circuit representation file to parse.')
    parser.add_argument('--output-file', '-o', type=str, required=True, help='The output C++ file.')
    parser.add_argument('--module-name', '-m', type=str, required=True, help='The name of the module to parse.')
    parser.add_argument('--output-format', '-f', type=str, required=True, help='Output format: asm or cpp.')

    # Parse the arguments
    args = parser.parse_args()

    # Read the file content
    fileContent = getContent(args.input_file)

    # Parser ctor
    parser = Parser(moduleName=args.module_name)

    # Parse the circuit representation
    parser.parse(fileContent)

    # Print the module
    # print("Info: Module name = ", parser.moduleName)
    # print("Info: Inputs = ", parser.inputsList)
    # print("Info: Outputs = ", parser.outputsList)
    # print("Info: Wires = ", parser.wireList)
    # print("\nInfo: Statements List")
    # for statement in parser.statementList:
        # print(statement.tostr())
    # print()

    # Generate the code
    code = ''
    if args.output_format == 'cpp':
        generator = Generator(parser)
        code = generator.generateCode()
    elif args.output_format == 'asm':
        generator = GeneratorAsm(parser)
        code = generator.generateCode()

    # Write the generated C++ code into a file
    writeToFile(args.output_file, code)

