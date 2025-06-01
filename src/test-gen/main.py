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
from function_signature_parser import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util import *

def splitModuleName(name):
    parts = name.split('__')
    if len(parts) != 4:
        raise ValueError(f"Invalid format: '{name}'. Expected format 'operation_datatype'.")
    arch, numRegs, pimMode = parts[:3]
    operator, dataType = parts[3].rsplit('_', 1)  # split by the last underscore
    return arch, numRegs, operator, dataType

def extractSignatureBlock(inputText):
    startToken = "// SIGNATURE_START"
    endToken = "// SIGNATURE_END"

    startIndex = inputText.find(startToken)
    endIndex = inputText.find(endToken)

    if startIndex == -1 or endIndex == -1 or startIndex >= endIndex:
        return None

    startIndex += len(startToken)
    return inputText[startIndex:endIndex].strip()

if __name__ == "__main__":
    # Set up argument parser with optional arguments
    parser = argparse.ArgumentParser(description='Generate PIMeval test code for bit-serial compiler micro-program output.')
    parser.add_argument('--module-name', '-m', type=str, required=True, help='The name of the module to parse. Format: <operation>_<datatype>, example: int_int32.')
    parser.add_argument('--output-path', '-o', type=str, required=True, help='The path where test cpp file and Makefile stored.')
    parser.add_argument('--num-tests', '-n', type=int, default=100, help='Number of test cases.')
    parser.add_argument('--pim-mode', '-p', type=str, default='digital', help='The PIM architecture mode (analog/digital).')
    parser.add_argument('--golden-function-path', '-g', type=str, default=None, help='The path to the golden function file hpp file.')

    # Parse the arguments
    args = parser.parse_args()

    # Resolve the operands list
    operator = None
    if args.golden_function_path is None:
        # Resolve operator and data type
        arch, numRegs, operator, dataType = splitModuleName(args.module_name)
        operandsListGenerator = OperandsListGenerator(operator, dataType)
        inputOperands, outputOperands = operandsListGenerator.getOperands()

        # Test Generator ctor
        testGenerator = TestGenerator(moduleName=args.module_name, outputPath=args.output_path, numTests=args.num_tests, inputOperands=inputOperands, outputOperands=outputOperands, operator=operator, pimMode=args.pim_mode)
    else:
        # Parse the golden model function signature
        goldenFunctionContent = getContent(args.golden_function_path)
        goldenFunctionSignature = extractSignatureBlock(goldenFunctionContent)

        functionSignatureParser = FunctionSignatureParser()
        inputOperands, outputOperands, functionName = functionSignatureParser.parse(goldenFunctionSignature)

        # Test Generator ctor
        testGenerator = TestGenerator(moduleName=args.module_name, outputPath=args.output_path, numTests=args.num_tests, inputOperands=inputOperands, outputOperands=outputOperands, operator=operator, pimMode=args.pim_mode, goldenFunctionFilePath=args.golden_function_path, goldenFunctionName=functionName)

    # Generate the Makefile
    writeToFile(args.output_path + "/" + "Makefile", testGenerator.generateMakeFile())

    # Generate the test CPP file
    writeToFile(args.output_path + "/" + args.module_name + ".test.cpp", testGenerator.generatCppTestFile())

    # Generate the bitwise test C file
    writeToFile(args.output_path + "/" + args.module_name + ".test_bitwise.c", testGenerator.generatBitwiseTestFile())

    # Generte the golden function hpp file
    if args.golden_function_path is None:
        writeToFile(args.output_path + "/" + testGenerator.resolveGoldenFunctionPath(), testGenerator.generateGoldenFunctionFile())

