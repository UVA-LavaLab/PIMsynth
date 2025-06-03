#usr/bin/env python3
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
import traceback

from test_gen import TestFileGeneratorBase, \
    MakeFileGenerator, \
    OperandsListGenerator, \
    TestFileGeneratorConfig, \
    PimTestGenerator, \
    BitwiseTestGenerator, \
    GoldenFunctionFileGenerator

from function_signature_parser import FunctionSignatureParser

# TODO: avoid importing util from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import util

class TestCodeGenerator:
    def __init__(self):
        "Initialize the code generator"
        self.module_name = ''
        self.output_path = ''
        self.num_tests = ''
        self.pim_mode = ''
        self.golden_function_file_name = ''
        self.debug = False

    def __parse_args(self, input_args):
        """ Parse command line arguments """
        arg_parser = argparse.ArgumentParser(
            description='Generate PIMeval test code for bit-serial compiler micro-program output.'
        )
        arg_parser.add_argument(
            '--module-name', '-m', type=str, required=True,
            help='The name of the module to parse. Format: <operation>_<dataType>, '
                 'example: int_int32. (It could be a custom name if the golden function path is passed.)'
        )
        arg_parser.add_argument(
            '--output-path', '-o', type=str, required=True,
            help='The path where test cpp file and Makefile stored.'
        )
        arg_parser.add_argument(
            '--num-tests', '-n', type=int, default=100,
            help='Number of test cases.'
        )
        arg_parser.add_argument(
            '--pim-mode', '-p', type=str, default='digital',
            help='The PIM architecture mode (analog/digital).'
        )
        arg_parser.add_argument(
            '--golden-function-file-name', '-g', type=str, default=None,
            help='The path to the golden function file hpp file.'
        )
        arg_parser.add_argument(
            '--debug', action='store_true', default=False,
            help='Enable debug mode'
        )

        args = arg_parser.parse_args(input_args)

        self.module_name = args.module_name
        self.output_path = args.output_path
        self.num_tests = args.num_tests
        self.pim_mode = args.pim_mode
        self.golden_function_file_name = args.golden_function_file_name
        self.debug = args.debug

    def __input_arguments_sanity_check(self):
        """ Sanity-check input arguments such as file existence and required paths """
        success = True
        if not self.golden_function_file_name is None:
            if not os.path.isfile(self.golden_function_file_name):
                print(f"Error: Input file '{self.golden_function_file_name}' does not exist.")
                success = False
        if not success:
            raise ValueError("Invalid command line arguments")

    def __split_module_name(self, name):
        """ parses the operator and data type based on the module name """
        parts = name.split('__')
        if len(parts) != 4:
            raise ValueError(f"Invalid format: '{name}'. Expected format 'operation_datatype'.")
        arch, num_regs, pim_mode = parts[:3]
        operator, data_type = parts[3].rsplit('_', 1)  # split by the last underscore
        return operator, data_type

    def __get_test_file_generator_config(self):
        """ Create the code generation's input token """
        function_name = None
        operator = None
        use_golden = self.golden_function_file_name is not None
        if use_golden:
            parser = FunctionSignatureParser()
            fileContent = util.getContent(self.golden_function_file_name)
            input_operands, output_operands, function_name = parser.parse(fileContent)
        else:
            operator, data_type = self.__split_module_name(self.module_name)
            generator = OperandsListGenerator(operator, data_type)
            input_operands, output_operands = generator.get_operands()

        return TestFileGeneratorConfig(
            module_name=self.module_name,
            output_path=self.output_path,
            num_tests=self.num_tests,
            input_operands=input_operands,
            output_operands=output_operands,
            operator=operator,
            pim_mode=self.pim_mode,
            golden_function_file_name=self.golden_function_file_name,
            golden_function_name=function_name
        )

    def __run_code_generation(self):
        "Run the test code generator"
        config = self.__get_test_file_generator_config()
        test_generator = TestFileGeneratorBase(config)

        if self.golden_function_file_name is None:
            golden_function_file_generator = GoldenFunctionFileGenerator(config)
            util.writeToFile(self.output_path + "/" + golden_function_file_generator.get_golden_function_file_name(), \
                             golden_function_file_generator.generate())

        bitwise_test_generator = BitwiseTestGenerator(config)
        util.writeToFile(self.output_path + "/" + bitwise_test_generator.get_bitwise_test_file_name(), \
                         bitwise_test_generator.generate())

        pim_test_generator = PimTestGenerator(config)
        util.writeToFile(self.output_path + "/" + pim_test_generator.get_pim_test_file_name(), pim_test_generator.generate())

        make_file_generator = MakeFileGenerator(config)
        util.writeToFile(self.output_path + "/" + make_file_generator.get_make_file_name(), make_file_generator.generate())

    def run(self, args):
        "Parse input arguments and generate the test code"
        self.__parse_args(args)
        self.__input_arguments_sanity_check()
        self.__run_code_generation()

# Main entry point
if __name__ == "__main__":
    test_code_generator = TestCodeGenerator()
    try:
        test_code_generator.run(sys.argv[1:])
        print("Info: Test Generation completed successfully.")
        sys.exit(0)
    except Exception as e:
        traceback.print_exc()
        print(f"Error: Test Generation failed: {e}")
        sys.exit(1)
