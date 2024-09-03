import sys
import argparse
from util import *
from parser import *

if __name__ == "__main__":
    # Set up argument parser with optional arguments
    parser = argparse.ArgumentParser(description='Parse Verilog code and extract module information.')
    parser.add_argument('--input-file', '-i', type=str, required=True, help='The input Verilog file to parse.')
    parser.add_argument('--module-name', '-m', type=str, required=True, help='The name of the module to parse.')

    # Parse the arguments
    args = parser.parse_args()

    # Read the file content
    fileContent = getContent(args.input_file)

    # Parser ctor
    verilog_parser = Parser(moduleName=args.module_name)

    # Parse the Verilog code
    verilog_parser.parse(fileContent)

    # Print the module
    print("Info: Module name = ", verilog_parser.moduleName)
    print("Info: Inputs = ", verilog_parser.inputsList)
    print("Info: Outputs = ", verilog_parser.outputsList)
    print("Info: Wires = ", verilog_parser.wireList)
    print("\nInfo: Statements List")
    for statement in verilog_parser.statementList:
        print(statement.tostr())
    print()

