#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: test_gen.py
Description: Geneates test cases to validate the functionality of the output of the bit-serial compiler using PIMeval
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Author: Deyuan Guo <guodeyuan@gmail.com> - Bit-wise C test code generation
Date: 2025-04-05
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util import *

class OperandsListGenerator():
    def __init__(self, operator, data_type):
        self.operator = operator
        self.data_type = data_type

    def __get_operands_count(self):
        one_operand = ["not", "abs", "popcount"]
        two_operand = ["add", "sub", "mul", "and", "or", "xor", "xnor", "mul", "min",
                      "max", "lt", "gt", "eq", "ne", "shift_l", "shift_r"]

        if self.operator in one_operand:
            return 1
        if self.operator in two_operand:
            return 2
        raise Exception(f"Error: operator {self.operator} is not handled.")

    def __get_inputs_list(self):
        if self.__get_operands_count() == 1: return [("a", self.data_type)]
        if self.__get_operands_count() == 2: return [("a", self.data_type), ("b", self.data_type)]
        raise Exception(f"Error: number of input operands is more than 2 which is not handled.")

    def __get_outputs_list(self):
        return [("z", self.data_type)]
        raise Exception(f"Error: number of input operands is more than 2 which is not handled.")

    def get_operands(self):
        """ Generate the list input and output operands """
        return self.__get_inputs_list(), self.__get_outputs_list()

class TestFileGeneratorConfig:
    def __init__(self, module_name, output_path, num_tests, input_operands,
                 output_operands, operator, pim_mode="digital",
                 golden_function_file_name=None, golden_function_name=None):
        self.module_name = module_name
        self.output_path = output_path
        self.num_tests = num_tests
        self.input_operands = input_operands
        self.output_operands = output_operands
        self.operator = operator
        self.pim_mode = pim_mode
        self.golden_function_file_name = golden_function_file_name
        self.golden_function_name = golden_function_name

    def get_module_name(self):
        return self.module_name

    def get_output_path(self):
        return self.output_path

    def get_num_tests(self):
        return self.num_tests

    def get_input_operands(self):
        return self.input_operands

    def get_output_operands(self):
        return self.output_operands

    def get_operator(self):
        return self.operator

    def get_pim_mode(self):
        return self.pim_mode

    def get_golden_function_file_name(self):
        return self.golden_function_file_name

    def get_golden_function_name(self):
        return self.golden_function_name

class TestFileGeneratorBase():
    def __init__(self, config: TestFileGeneratorConfig):
        self.module_name = config.get_module_name()
        self.output_path = config.get_output_path()
        self.num_tests = config.get_num_tests()
        self.input_operands = config.get_input_operands()
        self.output_operands = config.get_output_operands()
        self.operator = config.get_operator()
        self.pim_mode = config.get_pim_mode()
        self.golden_function_file_name = config.get_golden_function_file_name()
        self.golden_function_name = config.get_golden_function_name()

    def __get_c_data_type(self, data_type):
        if data_type in {"int1", "int2", "int3", "int4"}:
            return "int8_t"
        elif data_type in {"uint1", "uint2", "uint3", "uint4"}:
            return "uint8_t"
        return f"{data_type}_t"

    def __get_c_data_type_for_print(self, data_type):
        if data_type in {"int1", "int2", "int3", "int4", "int8"}:
            return "int16_t"
        elif data_type in {"uint1", "uint2", "uint3", "uint4", "uint8"}:
            return "uint16_t"
        return f"{data_type}_t"

    def _get_c_data_width(self, data_type):
        if data_type.startswith("int") and data_type[3:].isdigit():
            return int(data_type[3:])
        elif data_type.startswith("uint") and data_type[4:].isdigit():
            return int(data_type[4:])
        raise Exception(f"Unknown data type: {data_type}")

    def _get_inputs_list_string(self, with_type=False):
        inputs = [
            f"{self.__get_c_data_type(data_type)} {operand}" if with_type else operand
            for operand, data_type in self.input_operands
        ]
        return ", ".join(inputs)

    def _get_outputs_list_string(self, with_type=False, with_star=False, with_ampersand=False):
        output_parts = []
        for operand, data_type in self.output_operands:
            if with_type:
                ctype = self.__get_c_data_type(data_type)
                prefix = f"{ctype}* " if with_star else f"{ctype} "
                output_parts.append(f"{prefix}{operand}")
            else:
                if with_ampersand:
                    output_parts.append(f"&{operand}")
                elif with_star:
                    output_parts.append(f"*{operand}")
                else:
                    output_parts.append(operand)

        return ", ".join(output_parts)

    def _get_outputs_declaration_string(self, with_res_postfix=False):
        return "\n\t".join(
            f"{self.__get_c_data_type(data_type)} {operand}_res;" if with_res_postfix else \
                f"{self.__get_c_data_type(data_type)} {operand};"
            for operand, data_type in self.output_operands
        ) + ("\n\t" if self.output_operands else "")

    def _get_golden_function_name(self):
        if self.golden_function_name is None:
            return f"{self.module_name}_golden"
        return self.golden_function_name

    def _get_random_number_generation_string(self, c_style=False):
        code = ""
        randFunc = "rand()" if c_style else "std::rand()"
        for i, (operand, data_type) in enumerate(self.input_operands):
            if self.operator in ["shift_l", "shift_r"] and i == 1:
                bound = self._get_c_data_width(data_type)  # limit the shift amount to the data width
            else:
                bound = 2 ** self._get_c_data_width(data_type)
            code += f"{self.__get_c_data_type(data_type)} {operand} = {randFunc} % {bound};\n\t\t"
        return code

    def __get_print_all_operands_string(self, c_style=False):
        def get_print_format(data_type):
            format_dict = {
                "int1": "%d",
                "int2": "%d",
                "int3": "%d",
                "int4": "%d",
                "int8": "%d",
                "int16": "%d",
                "int32": "%d",
                "int64": "%ld",
                "uint8": "%u",
                "uint16": "%u",
                "uint32": "%u",
                "uint64": "%lu",
                "float": "%f",
                "double": "%lf",
            }
            return format_dict.get(data_type, "%d")  # default to %d

        code = ""
        for (operand, data_type) in self.input_operands:
            if c_style:
                fmt = get_print_format(data_type)
                code += f'printf("{operand}: {fmt}\\n", ({self.__get_c_data_type_for_print(data_type)}) {operand});\n\t'
            else:
                code += f'std::cerr << "{operand}: " << ({self.__get_c_data_type_for_print(data_type)}) {operand} << std::endl;\n\t'

        for (operand, data_type) in self.output_operands:
            if c_style:
                fmt = get_print_format(data_type)
                code += f'printf("{operand}(expected): {fmt}\\n", ({self.__get_c_data_type_for_print(data_type)}) {operand});\n\t'
                code += f'printf("{operand}(pim     ): {fmt}\\n", ({self.__get_c_data_type_for_print(data_type)}) {operand}_res);\n\t'
            else:
                code += f'std::cerr << "{operand}(expected): " << ({self.__get_c_data_type_for_print(data_type)}) {operand} << std::endl;\n\t'
                code += f'std::cerr << "{operand}(pim     ): " << ({self.__get_c_data_type_for_print(data_type)}) {operand}_res << std::endl;\n\t'
        return code

    def _get_verification_code_string(self, c_style=False):
        code = ""
        for (operand, data_type) in self.output_operands:
            code += f"""
    if ({operand} != {operand}_res) {{
        {self.__get_print_all_operands_string(c_style)}
        return false;
    }}
            """
        return code

    def get_golden_function_file_name(self):
        golden_function_file_name = f"{self.module_name}.golden.hpp"
        if not self.golden_function_file_name is None:
            golden_function_file_name = self.golden_function_file_name
        return golden_function_file_name

    def get_bitwise_test_file_name(self):
        return f"{self.module_name}.test_bitwise.cpp"

    def get_bitwise_executable_file_name(self):
        return f"{self.module_name}.test_bitwise.out"

    def get_pim_test_file_name(self):
        return f"{self.module_name}.test.cpp"

    def get_pim_executable_file_name(self):
        return f"{self.module_name}.test.out"

    def get_module_name(self):
        return self.module_name

class GoldenFunctionFileGenerator(TestFileGeneratorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __get_bound(self):
        data_type = self.output_operands[0][1]
        return 2 ** self._get_c_data_width(data_type)

    def __get_golden_function_statement(self, operator):
        operand = self.output_operands[0][0]
        data_type = self.output_operands[0][1]
        op_dict = {
            "add": f'a + b',
            "sub": f'a - b',
            "mul": f'a * b',
            "and": f'a & b',
            "or": f'a | b',
            "xor": f'a ^ b',
            "xnor": f'~(a ^ b)',
            "max": f'(a > b)?a:b',
            "min": f'(a < b)?a:b',
            "abs": f'(a > 0)?a:-a',
            "not": f'~a',
            "lt": f'(a < b)',
            "gt": f'(a > b)',
            "eq": f'(a == b)',
            "ne": f'(a != b)',
            "popcount": f'std::bitset<{data_type[3:]}>(a).count()' if data_type else None,
            "shift_l": f'a << b',
            "shift_r": f'a >> b',
        }

        expression = op_dict.get(operator)
        if expression is None:
            return None
        return f"*{operand} = ({expression}) % {self.__get_bound()};"

    def generate(self):
        if not self.golden_function_file_name is None:
            code = getContent(self.goldenModelHeaderFile)
        else:
            outputOperandType = self.output_operands[0][1]
            functionName = self._get_golden_function_name()
            code = f"#ifndef {functionName.upper()}_H\n"
            code += f"#define {functionName.upper()}_H\n"
            signature = f"void {functionName}({self._get_inputs_list_string(with_type=True)}, {self._get_outputs_list_string(with_type=True, with_star=True)})"
            testStatmentStr = self.__get_golden_function_statement(self.operator)
            if testStatmentStr is None:
                raise Exception("Error: The test generator does not support {self.operator} operator.")
            code += f"""
    {signature} {{
      {testStatmentStr}
      return;
    }}\n\n
    """
            code += "#endif\n\n"
        return code

class BitwiseTestGenerator(TestFileGeneratorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __get_bitwise_function_call(self):
        """ Call the bitwise function """
        code = ''
        params = ''

        # Generate the bit_* array for the input operands
        for (operand, data_type) in self.input_operands:
            data_width = self._get_c_data_width(data_type)
            code += f"""
            int bit_{operand}[{data_width}];
            for (int i = 0; i < {data_width}; i++) {{
                bit_{operand}[i] = {operand} & (1 << i) ? 1 : 0;
            }}
            """
            for i in range(data_width):
                params += f'bit_{operand}+{i}, '

        # Call the bitwise function
        for (operand, data_type) in self.output_operands:
            data_width = self._get_c_data_width(data_type)
            code += f'\tint {operand}_bit_out[{data_width}];\n'
            for i in range(data_width):
                params += f'{operand}_bit_out+{i}, '

        params = params[:-2] # remove last comma and space
        code += f'\t{self.module_name}({params});'

        # Cast *_bit_out array to the output operands
        for (operand, data_type) in self.output_operands:
            data_width = self._get_c_data_width(data_type)
            code += f"""
        {operand}_res = 0;
        for (int i = 0; i < {data_width}; i++) {{
            {operand}_res |= {operand}_bit_out[i] << i;
        }}
            """
        return code

    def generate(self):
        """ Generate test file for bitwise IR """
        golden_function_file_name = self.get_golden_function_file_name()
        inputs_string_with_type = self._get_inputs_list_string(with_type=True)
        inputs_string = self._get_inputs_list_string()
        random_number_generation_string = self._get_random_number_generation_string(c_style=True)
        bitwise_function_call = self.__get_bitwise_function_call()
        outputs_declaration_string = self._get_outputs_declaration_string()
        outputs_declaration_string_with_result_postfix = self._get_outputs_declaration_string(with_res_postfix=True)
        outputs_string_with_ampersand = self._get_outputs_list_string(with_ampersand=True)

        code = f"""
// Automatically generated by bit-serial compiler
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <time.h>
#include "{self.module_name}.bitwise.c"
#include "{golden_function_file_name}"

bool runTest({inputs_string_with_type}) {{
    // Calculate the expected result using the golden model
    {outputs_declaration_string}
    {outputs_declaration_string_with_result_postfix}
    {self._get_golden_function_name()}({inputs_string}, {outputs_string_with_ampersand});

    {bitwise_function_call}

    {self._get_verification_code_string(c_style=True)}

    return true;
}}

int main() {{
    printf("Info: Running test for bitwise IR of {self.module_name}\\n");

    // Initialize random seed
    srand((unsigned int)time(NULL));

    // Run random tests
    int num_tests = {self.num_tests};  // Number of random test cases
    bool allPassed = true;
    for (int testNumber = 1; testNumber <= num_tests; ++testNumber) {{
        {random_number_generation_string}

        bool ok = runTest({inputs_string});
        allPassed &= ok;
        if (!ok) {{
            printf("Error: Test %d failed!\\n", testNumber);
        }} else {{
            printf("Info: Test %d passed!\\n", testNumber);
        }}
    }}
    if (allPassed) {{
        printf("Bitwise test: OK\\n");
    }} else {{
        printf("Bitwise test: NOT OK\\n");
    }}

    return 0;
}}
"""
        return code

class PimTestGenerator(TestFileGeneratorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __get_pim_copy_host_to_device_string(self):
        code = ""
        for (operand, data_type) in self.input_operands:
            code += f"pimCopyHostToDevice(&{operand}, {operand}Pim);\n\t"
        return code

    def __get_pim_copy_device_to_host(self):
        code = ""
        for (operand, data_type) in self.output_operands:
            code += f"pimCopyDeviceToHost({operand}Pim, &{operand}_res);\n\t"
        return code

    def __get_pim_alloc_string(self):
        code = ""
        firstObj = f"{self.input_operands[0][0]}Pim"
        firstObjDataType = self.input_operands[0][1]
        code += f"PimObjId {firstObj} = pimAlloc(PIM_ALLOC_V, 1, {self.__get_pim_eval_data_type(firstObjDataType)});\n\t"
        for (operand, data_type) in self.input_operands[1:] + self.output_operands:
            obj = f"{operand}Pim"
            code += f"PimObjId {obj} = pimAllocAssociated({firstObj}, {self.__get_pim_eval_data_type(data_type)});\n\t"
        return code

    def __get_pim_eval_data_type(self, data_type):
        if data_type in {"int1", "int2", "int3", "int4", "int8"}:
            return "PIM_INT8"
        elif data_type in {"uint1", "uint2", "uint3", "uint4", "uint8"}:
            return "PIM_UINT8"
        if data_type.startswith("int") or data_type.startswith("uint"):
            return f"PIM_{data_type.upper()}"
        raise ValueError(f"Unknown data type: {data_type}")

    def __get_pim_objects_list(self, with_type=False):
        return [f"PimObjId {operand}Pim" if with_type else f"{operand}Pim" \
                for operand, _ in self.input_operands + self.output_operands]

    def __get_pim_objects_string(self, with_type=False):
        return ", ".join(self.__get_pim_objects_list(with_type))

    def __get_pim_free_string(self):
        code = ""
        for objStr in self.__get_pim_objects_list():
            code += f"pimFree({objStr});\n\t"
        return code

    def __get_pim_device(self):
        if self.pim_mode == "digital":
            return "PIM_DEVICE_BITSIMD_V"
        return "PIM_DEVICE_SIMDRAM"

    def generate(self):
        golden_function_file_name = self.get_golden_function_file_name()
        inputs_string_with_type = self._get_inputs_list_string(with_type=True)
        pim_objects_string_with_type = self.__get_pim_objects_string(with_type=True)
        inputs_string = self._get_inputs_list_string()
        outputs_string_with_ampersand = self._get_outputs_list_string(with_ampersand=True)
        pim_copy_host_to_device_string = self.__get_pim_copy_host_to_device_string()
        pim_copy_device_to_host_string = self.__get_pim_copy_device_to_host()

        pim_objects_string = self.__get_pim_objects_string()
        outputs_declaration_string = self._get_outputs_declaration_string()
        outputs_declaration_string_with_result_postfix = self._get_outputs_declaration_string(with_res_postfix=True)
        pim_alloc_string = self.__get_pim_alloc_string()
        random_number_generation_string = self._get_random_number_generation_string()
        pim_free_string = self.__get_pim_free_string()
        pim_device = self.__get_pim_device()

        code = f"""
// Automatically generated by bit-serial compiler
#include <iostream>
#include <cstdlib>
#include <ctime>
#include <cstdint>
#include <bitset>
#include "{self.get_module_name()}.hpp"
#include "{golden_function_file_name}"
#include "libpimeval.h"

bool runTest({inputs_string_with_type}, {pim_objects_string_with_type}) {{
  // Declare the output signals
  {outputs_declaration_string}
  {outputs_declaration_string_with_result_postfix}

  // Calculate the expected result using the golden model
  {self._get_golden_function_name()}({inputs_string}, {outputs_string_with_ampersand});

  // Copy data to PIM device
  {pim_copy_host_to_device_string}

  // Call the function under test
  {self.module_name}({pim_objects_string});

  // Retrieve and verify the result from the PIM device
  {pim_copy_device_to_host_string}

  {self._get_verification_code_string()}
  return true;
}}

int main() {{
  // Initialize random seed
  std::srand(static_cast<unsigned int>(std::time(nullptr)));

  // Initialize PIM device
  PimStatus status = pimCreateDevice({pim_device}, 1, 1, 2, 1024, 1024);
  if (status != PIM_OK) {{
      std::cerr << "Error: Failed to create PIM device with default config" << std::endl;
      return -1;
  }}

  // Allocate PIM objects for the input/output vector with element size = 1
  {pim_alloc_string}

  // Run random tests
  int num_tests = {self.num_tests};  // Number of random test cases
  bool allPassed = true;
  for (int testNumber = 1; testNumber <= num_tests; ++testNumber) {{
      {random_number_generation_string}

      pimResetStats();
      bool ok = runTest({inputs_string}, {pim_objects_string});
      allPassed &= ok;
      if (!ok) {{
          std::cerr << "Error: Test " << testNumber << " failed!" << std::endl;
      }} else {{
          std::cout << "Info: Test " << testNumber << " passed!" << std::endl;
      }}
  }}

  pimShowStats();
  if (allPassed) {{
      std::cout << "PIM test: ALL PASSED!" << std::endl;
  }} else {{
      std::cerr << "PIM test: SOME FAILED!" << std::endl;
  }}

  // Clean up and free allocated resources
  {pim_free_string}
  pimDeleteDevice();

  return 0;
}}

"""
        return code

class MakeFileGenerator(TestFileGeneratorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_make_file_name(self):
        return "Makefile"

    def generate(self):
        """ Generate Makefile """
        return f"""
# Automatically generated by bit-serial compiler

REPO_ROOT := $(shell git rev-parse --show-toplevel)
LIB_PIMEVAL_PATH := $(REPO_ROOT)/PIMeval-PIMbench/libpimeval

GCC = gcc
CXX = g++
CXXFLAGS = -I$(LIB_PIMEVAL_PATH)/include # Path to header files
LDFLAGS = -L$(LIB_PIMEVAL_PATH)/lib -l:libpimeval.a # Path to static library and linking

TARGET_PIM = {self.get_pim_executable_file_name()}
TARGET_BITWISE = {self.get_bitwise_executable_file_name()}

all: $(TARGET_PIM) $(TARGET_BITWISE)

$(TARGET_PIM): {self.get_pim_test_file_name()}
	$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS)

$(TARGET_BITWISE): {self.get_bitwise_test_file_name()}
	$(GCC) $< -o $@

clean:
	rm -f $(TARGET_PIM) $(TARGET_BITWISE)
"""
