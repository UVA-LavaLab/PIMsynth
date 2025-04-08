#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: main.py
Description: test generator using PIMeval API
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Date: 2025-04-05
"""

import sys
import os
import argparse
from test_gen import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util import *
if __name__ == "__main__":
    # Set up argument parser with optional arguments
    parser = argparse.ArgumentParser(description='Parse RISV assembly and generate either bit-serial assembly or PIMeval API function.')
    parser.add_argument('--module-name', '-m', type=str, required=True, help='The name of the module to parse. Format: <operation>_<datatype>, example: int_int32.')
    parser.add_argument('--output-path', '-o', type=str, required=True, help='The path where test cpp file and Makefile stored.')

    # Parse the arguments
    args = parser.parse_args()

    print(f"DEBUG: {args.module_name}")
    print(f"DEBUG: {args.output_path}")

    # Test Generator ctor
    testGenerator = TestGenerator(moduleName=args.module_name, outputPath=args.output_path)

    # Generate the Makefile
    writeToFile(args.output_path + "/" + "Makefile", testGenerator.generateMakeFile())

    # Generate the test CPP file
    writeToFile(args.output_path + "/" + args.module_name + "_test.cpp", testGenerator.generatCppTestFile())



