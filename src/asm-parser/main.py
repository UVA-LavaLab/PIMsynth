
import sys
import argparse
import os
from parser import *

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

    # Print Statement List
    parser.printStatementList()


