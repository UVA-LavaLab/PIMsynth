#include <iostream>
#include <cstdlib>
#include <ctime>
#include "tmp.hpp"
#include "libpimeval.h"

int funcGoldenModel(int num) {
    int count = 0;
    while (num) {
        count += num & 1; // Add 1 if the least significant bit is set
        num >>= 1;        // Shift the number right by 1
    }
    return count;
}

void runTest(int testNumber, int a, PimObjId aPim, PimObjId resultPim) {
    // Calculate the expected result using the golden model
    int expectedResult = funcGoldenModel(a);

    // Copy data to PIM device
    pimCopyHostToDevice(&a, aPim);

    // Call the function under test
    func(aPim, resultPim);

    // Retrieve and verify the result from the PIM device
    int pimResult;
    pimCopyDeviceToHost(resultPim, &pimResult);

    // Verify the result
    if (pimResult % 16 != expectedResult % 16) {
        // Print all inputs and outputs if there is a mismatch
        std::cerr << "Error: Test " << testNumber << " failed!" << std::endl;
        std::cerr << "  Input a = " << a << std::endl;
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
    PimObjId aPim = pimAlloc(PIM_ALLOC_V, 1, PIM_UINT8);
    PimObjId resultPim = pimAlloc(PIM_ALLOC_V, 1, PIM_UINT8);

    // Run random tests
    int testNumber = 1;
    int numTests = 100;  // Number of random test cases
    for (int t = 0; t < numTests; ++t) {
        int a = std::rand() % 256;  // Generate random 8-bit value for a
        runTest(testNumber++, a, aPim, resultPim);
    }

    // Clean up and free allocated resources
    pimFree(aPim);
    pimFree(resultPim);
    pimDeleteDevice();

    return 0;
}

