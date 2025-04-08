#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: test_gen.py
Description: Geneates test cases to validate the functionality of the output of the bit-serial compiler using PIMeval
Author: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
Date: 2025-04-05
"""

class TestGenerator:
    def __init__(self, moduleName, outputPath, numTests):
        self.moduleName = moduleName
        self.outputPath = outputPath
        self.numTests = numTests
        self.arch, self.numRegs, self.operator, self.dataType = self.splitModuleName(self.moduleName)

    def splitModuleName(self, name):
        parts = name.split('__')
        if len(parts) != 3:
            raise ValueError(f"Invalid format: '{name}'. Expected format 'operation_datatype'.")
        arch, numRegs = parts[:2]
        operator, dataType = parts[2].split('_')
        return arch, numRegs, operator, dataType

    def generateMakeFile(self):
        makefileStr = f"""
REPO_ROOT := $(shell git rev-parse --show-toplevel)
LIB_PIMEVAL_PATH := $(REPO_ROOT)/PIMeval-PIMbench/libpimeval

# Compiler and flags
CXX = g++
CXXFLAGS = -I$(LIB_PIMEVAL_PATH)/include # Path to header files
LDFLAGS = -L$(LIB_PIMEVAL_PATH)/lib -l:libpimeval.a # Path to static library and linking

# Target executable
TARGET = {self.moduleName}_test.out

# Source files
SRCS = {self.moduleName}_test.cpp

# Object files
OBJS = $(SRCS:.cpp=.o)

# Default target
all: $(TARGET)

# Rule to link the program
$(TARGET): $(OBJS)
	$(CXX) $(OBJS) -o $(TARGET) $(LDFLAGS)

# Rule to compile source files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean the build
clean:
	rm -f $(OBJS) $(TARGET)

"""
        return makefileStr

    def getGoldenFunctionStatement(self, operator):
        opDict = {
            "add": f'return a + b;',
            "sub": f'return a - b;',
            "min": f'return (a > b)?a:b;',
            "max": f'return (a < b)?a:b;',
        }
        return opDict[operator]

    def getCDatatype(self):
        lookupDict = {
            "int32" : "int",
            "int8" : "char",
        }
        return lookupDict[self.dataType]

    def getPimEvalDataType(self):
        lookupDict = {
            "int32" : "PIM_INT32",
            "int8" : "PIM_INT8",
        }
        return lookupDict[self.dataType]

    def getOperandsCount(self):
        oneOperand = ["not", "abs", "popcount"]
        twoOperand = ["add", "and", "or", "xor", "mul", "min", "max"]

        if self.operator in oneOperand:
            return 1
        if self.operator in twoOperand:
            return 2
        raise Exception(f"Error: operator {operator} is not handled.")

    def getInputsList(self):
        if self.getOperandsCount() == 1: return ["a"]
        if self.getOperandsCount() == 2: return ["a", "b"]
        raise Exception(f"Error: number of input operands is more than 2 which is not handled.")

    def getPimObjList(self):
        lst = []
        for item in self.getInputsList():
            lst.append(item + "Pim")
        return lst

    def getInputsStr(self):
        returnStr = ""
        i = 0
        for inputStr in self.getInputsList():
            returnStr += f"{inputStr}"
            if (i != len(self.getInputsList()) - 1):
                returnStr += ", "
            i+= 1
        return returnStr

    def getPimObjsStr(self):
        returnStr = ""
        i = 0
        for inputStr in self.getInputsList():
            returnStr += f"{inputStr}Pim"
            if (i != len(self.getInputsList()) - 1):
                returnStr += ", "
            i+= 1
        return returnStr

    def getInputsStrWithType(self):
        returnStr = ""
        i = 0
        for inputStr in self.getInputsList():
            returnStr += f"{self.getCDatatype()} {inputStr}"
            if (i != len(self.getInputsList()) - 1):
                returnStr += ", "
            i+= 1
        return returnStr

    def getPimObjStrWithType(self):
        returnStr = ""
        i = 0
        for objStr in self.getPimObjList():
            returnStr += f"PimObjId {objStr}"
            if (i != len(self.getPimObjList()) - 1):
                returnStr += ", "
            i+= 1
        return returnStr

    def getGoldenFunctionStr(self):
        funcSignatureStr = f"{self.getCDatatype()} funcGoldenModel({self.getInputsStrWithType()})"
        testStatmentStr = self.getGoldenFunctionStatement(self.operator)
        returnStr = f"""
{funcSignatureStr} {{
  {testStatmentStr}
}}
        """
        return returnStr

    def getPimCopyHosttoDeviceStr(self):
        returnStr = ""
        for inputStr in self.getInputsList():
            returnStr += f"pimCopyHostToDevice(&{inputStr}, {inputStr}Pim);\n\t"
        return returnStr

    def getCoutStr(self):
        returnStr = ""
        i = 0
        for inputStr in self.getInputsList():
            returnStr += f"\"Input {inputStr} = \" << {inputStr} << "
            if (i != len(self.getInputsList()) - 1):
                returnStr += "\", \" << "
            i+= 1
        return returnStr

    def getPimAllocStr(self):
        returnStr = ""
        for objStr in self.getPimObjList():
            returnStr += f"PimObjId {objStr} = pimAlloc(PIM_ALLOC_V, 1, {self.getPimEvalDataType()});\n\t"
        return returnStr

    def getRandGenStr(self):
        returnStr = ""
        for inputStr in self.getInputsList():
            returnStr += f"{self.getCDatatype()} {inputStr} = std::rand();\n\t"
        return returnStr

    def getPimFreeStr(self):
        returnStr = ""
        for objStr in self.getPimObjList():
            returnStr += f"pimFree({objStr});\n\t"
        return returnStr

    def generatCppTestFile(self):
        goldenFunctionStr = self.getGoldenFunctionStr()
        inputsStrWithType = self.getInputsStrWithType()
        pimObjStrWithType = self.getPimObjStrWithType()
        inputsStr = self.getInputsStr()
        pimCopyHostToDeviceStr = self.getPimCopyHosttoDeviceStr()
        pimObjsStr = self.getPimObjsStr()
        coutStr = self.getCoutStr()
        pimAllocStr = self.getPimAllocStr()
        randGenStr = self.getRandGenStr()
        pimFreeStr = self.getPimFreeStr()

        testFileStr = f"""
#include <iostream>
#include <cstdlib>
#include <ctime>
#include "{self.moduleName}.hpp"
#include "libpimeval.h"

{goldenFunctionStr}

void runTest(int testNumber, {inputsStrWithType}, {pimObjStrWithType}, PimObjId resultPim) {{
  // Calculate the expected result using the golden model
  int expectedResult = funcGoldenModel({inputsStr});

  // Copy data to PIM device
  {pimCopyHostToDeviceStr}

  // Call the function under test
  {self.moduleName}({pimObjsStr}, resultPim);

  // Retrieve and verify the result from the PIM device
  int pimResult;
  pimCopyDeviceToHost(resultPim, &pimResult);

  // Verify the result
  if (pimResult != expectedResult) {{
      // Print all inputs and outputs if there is a mismatch
      std::cerr << "Error: Test " << testNumber << " failed!" << std::endl;
      std::cerr << {coutStr} std::endl;
      std::cerr << "  Expected result = " << expectedResult << ", PIM result = " << pimResult << std::endl;
  }} else {{
      std::cout << "Info: Test " << testNumber << " passed!" << std::endl;
  }}
}}

int main() {{
  // Initialize random seed
  std::srand(static_cast<unsigned int>(std::time(nullptr)));

  // Initialize PIM device
  //PimStatus status = pimCreateDeviceFromConfig(PIM_DEVICE_BITSIMD_V, nullptr);
  PimStatus status = pimCreateDevice(PIM_DEVICE_BITSIMD_V, 1, 1, 2, 1024, 1024);
  if (status != PIM_OK) {{
      std::cerr << "Error: Failed to create PIM device with default config" << std::endl;
      return -1;
  }}

  // Allocate PIM objects for the 32-bit input/output ports with element size = 1
  {pimAllocStr}
  PimObjId resultPim = pimAlloc(PIM_ALLOC_V, 1, {self.getPimEvalDataType()});

  // Run random tests
  int testNumber = 1;
  int numTests = {self.numTests};  // Number of random test cases
  for (int t = 0; t < numTests; ++t) {{
      {randGenStr}

      runTest(testNumber++, {inputsStr}, {pimObjsStr}, resultPim);
  }}

  // Clean up and free allocated resources
  {pimFreeStr}
  pimFree(resultPim);
  pimDeleteDevice();

  return 0;
}}

"""


        return testFileStr

