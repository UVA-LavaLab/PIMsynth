#include <iostream>
#include <cstdlib>
#include <ctime>
#include <cmath> // For std::abs
#include "tmp.hpp"
#include "libpimeval.h"

// Function to compare two floating-point numbers with a given error tolerance
bool areEqualWithError(double num1, double num2, double error) {
    if (error < 0) {
        throw std::invalid_argument("Error tolerance must be non-negative.");
    }
    return std::abs(num1 - num2) <= error;
}

// 32-bit golden model function
float funcGoldenModel(float a, float b) {
    return a * b;
}

void runTest(int testNumber, float a, float b, PimObjId aPim, PimObjId bPim, PimObjId resultPim) {
    // Calculate the expected result using the golden model
    float expectedResult = funcGoldenModel(a, b);

    // Copy data to PIM device
    pimCopyHostToDevice(&a, aPim);
    pimCopyHostToDevice(&b, bPim);

    // Call the function under test
    func(aPim, bPim, resultPim);

    // Retrieve and verify the result from the PIM device
    float pimResult;
    pimCopyDeviceToHost(resultPim, &pimResult);

    // Verify the result
    if (areEqualWithError(pimResult, expectedResult, 1e-9)) {
        // Print all inputs and outputs if there is a mismatch
        std::cerr << "Error: Test " << testNumber << " failed!" << std::endl;
        std::cerr << "  Input a = " << a << ", b = " << b << std::endl;
        std::cerr << "  Expected result = " << expectedResult << ", PIM result = " << pimResult << std::endl;
    } else {
        std::cout << "Info: Test " << testNumber << " passed!" << std::endl;
    }
}

int main() {
    // Initialize random seed
    std::srand(static_cast<unsigned int>(std::time(nullptr)));

    // Initialize PIM device
    PimStatus status = pimCreateDeviceFromConfig(PIM_DEVICE_BITSIMD_V, nullptr);
    if (status != PIM_OK) {
        std::cerr << "Error: Failed to create PIM device with default config" << std::endl;
        return -1;
    }

    // Allocate PIM objects for the 32-bit input/output ports with element size = 1
    PimObjId aPim = pimAlloc(PIM_ALLOC_V, 1, PIM_FP32);
    PimObjId bPim = pimAlloc(PIM_ALLOC_V, 1, PIM_FP32);
    PimObjId resultPim = pimAlloc(PIM_ALLOC_V, 1, PIM_FP32);

    // Run random tests
    int testNumber = 1;
    int numTests = 100;  // Number of random test cases
    for (int t = 0; t < numTests; ++t) {
        float a = std::rand();  // Generate random 32-bit value for a
        float b = std::rand();  // Generate random 32-bit value for b

        runTest(testNumber++, a, b, aPim, bPim, resultPim);
    }

    // Clean up and free allocated resources
    pimFree(aPim);
    pimFree(bPim);
    pimFree(resultPim);
    pimDeleteDevice();

    return 0;
}

