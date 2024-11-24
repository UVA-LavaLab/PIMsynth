#include <iostream>
#include <cstdlib>
#include <ctime>
#include "tmp.hpp"
#include "libpimeval.h"

// 32-bit golden model function
int funcGoldenModel(int a, int b) {
    return a + b;
}

void runTest(int testNumber, int a, int b, PimObjId aPim, PimObjId bPim, PimObjId resultPim) {
    // Calculate the expected result using the golden model
    int expectedResult = funcGoldenModel(a, b);

    // Copy data to PIM device
    pimCopyHostToDevice(&a, aPim);
    pimCopyHostToDevice(&b, bPim);

    // Call the function under test
    func(aPim, bPim, resultPim);

    // Retrieve and verify the result from the PIM device
    int pimResult;
    pimCopyDeviceToHost(resultPim, &pimResult);

    // Verify the result
    if (pimResult != expectedResult) {
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
    //PimStatus status = pimCreateDeviceFromConfig(PIM_DEVICE_BITSIMD_V, nullptr);
    PimStatus status = pimCreateDevice(PIM_DEVICE_BITSIMD_V, 1, 1, 2, 1024, 1024);
    if (status != PIM_OK) {
        std::cerr << "Error: Failed to create PIM device with default config" << std::endl;
        return -1;
    }

    // Allocate PIM objects for the 32-bit input/output ports with element size = 1
    PimObjId aPim = pimAlloc(PIM_ALLOC_V, 1, PIM_INT32);
    PimObjId bPim = pimAlloc(PIM_ALLOC_V, 1, PIM_INT32);
    PimObjId resultPim = pimAlloc(PIM_ALLOC_V, 1, PIM_INT32);

    // Run random tests
    int testNumber = 1;
    int numTests = 100;  // Number of random test cases
    for (int t = 0; t < numTests; ++t) {
        int a = std::rand();  // Generate random 32-bit value for a
        int b = std::rand();  // Generate random 32-bit value for b

        runTest(testNumber++, a, b, aPim, bPim, resultPim);
    }

    // Clean up and free allocated resources
    pimFree(aPim);
    pimFree(bPim);
    pimFree(resultPim);
    pimDeleteDevice();

    return 0;
}

