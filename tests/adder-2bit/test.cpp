#include <iostream>
#include <cstdlib>
#include <ctime>
#include <cassert>
#include <cstring>
#include "tmp.hpp"
#include "libpimeval.h"

// Golden model function for 2-bit adder
void funcGoldenModel(
   int a0,
   int a1,
   int b0,
   int b1,
   int cin,
   int& cout,
   int& sum0,
   int& sum1
) {
   // Pack the input bits into integers
   int a = (a0 << 0) | (a1 << 1);
   int b = (b0 << 0) | (b1 << 1);
   
   // Perform the arithmetic operation on the packed data
   unsigned int result = a + b + cin;
   
   // Expand the result into separate bits
   sum0 = (result >> 0) & 1;
   sum1 = (result >> 1) & 1;
   cout = (result >> 2) & 1;
}

void runTest(int testNumber, PimObjId a0Pim, PimObjId a1Pim, PimObjId b0Pim, PimObjId b1Pim, PimObjId cinPim, PimObjId sum0Pim, PimObjId sum1Pim, PimObjId coutPim) {
    // Generate random input values
    int a0 = std::rand() % 2;
    int a1 = std::rand() % 2;
    int b0 = std::rand() % 2;
    int b1 = std::rand() % 2;
    int cin = std::rand() % 2;
    int sum0, sum1, cout;

    std::cout << "Info: Test " << testNumber << ": a0 = " << a0 << ", a1 = " << a1 << ", b0 = " << b0 << ", b1 = " << b1 << ", cin = " << cin << std::endl;

    // Calculate golden model results
    funcGoldenModel(a0, a1, b0, b1, cin, cout, sum0, sum1);

    // Copy data to PIM device
    pimCopyHostToDevice(&a0, a0Pim);
    pimCopyHostToDevice(&a1, a1Pim);
    pimCopyHostToDevice(&b0, b0Pim);
    pimCopyHostToDevice(&b1, b1Pim);
    pimCopyHostToDevice(&cin, cinPim);

    // Call the function under test
    func(a0Pim, a1Pim, b0Pim, b1Pim, cinPim, coutPim, sum0Pim, sum1Pim);

    // Retrieve results and compare
    int pimSum0, pimSum1, pimCout;
    pimCopyDeviceToHost(sum0Pim, &pimSum0);
    pimCopyDeviceToHost(sum1Pim, &pimSum1);
    pimCopyDeviceToHost(coutPim, &pimCout);

    if (pimSum0 == sum0 && pimSum1 == sum1 && pimCout == cout) {
        std::cout << "Info: Test " << testNumber << " passed!" << std::endl;
    } else {
        std::cerr << "Error: Test " << testNumber << " failed!" << std::endl;
        std::cerr << "Expected sum0: " << sum0 << ", PIM sum0: " << pimSum0 << std::endl;
        std::cerr << "Expected sum1: " << sum1 << ", PIM sum1: " << pimSum1 << std::endl;
        std::cerr << "Expected cout: " << cout << ", PIM cout: " << pimCout << std::endl;
    }
}

int main(int argc, char* argv[]) {
    // Step 1: Parse and validate the configurable test count from command-line arguments
    int testCount = 10;  // Default value if not provided
    if (argc > 1) {
        testCount = std::atoi(argv[1]);
        if (testCount <= 0) {
            std::cerr << "Error: Test count must be a positive integer." << std::endl;
            return -1;
        }
    }

    // Step 2: Initialize random seed
    std::srand(static_cast<unsigned>(std::time(0)));

    // Step 3: Create the PIM device using pimCreateDeviceFromConfig with null configFileName
    PimStatus status = pimCreateDeviceFromConfig(PIM_DEVICE_BITSIMD_V, nullptr);
    if (status != PIM_OK) {
        std::cerr << "Error: Failed to create PIM device using default config" << std::endl;
        return -1;
    }
    std::cout << "Info: Successfully created PIM device with default configuration." << std::endl;

    // Step 4: Allocate PIM objects for the input/output ports
    PimObjId a0Pim = pimAlloc(PIM_ALLOC_V, 1, PIM_INT32);
    PimObjId a1Pim = pimAllocAssociated(a0Pim, PIM_INT32);
    PimObjId b0Pim = pimAllocAssociated(a0Pim, PIM_INT32);
    PimObjId b1Pim = pimAllocAssociated(a0Pim, PIM_INT32);
    PimObjId cinPim = pimAllocAssociated(a0Pim, PIM_INT32);
    PimObjId sum0Pim = pimAllocAssociated(a0Pim, PIM_INT32);
    PimObjId sum1Pim = pimAllocAssociated(a0Pim, PIM_INT32);
    PimObjId coutPim = pimAllocAssociated(a0Pim, PIM_INT32);

    // Step 5: Run the configurable number of test cases
    for (int i = 0; i < testCount; ++i) {
        runTest(i + 1, a0Pim, a1Pim, b0Pim, b1Pim, cinPim, sum0Pim, sum1Pim, coutPim);
    }

    // Step 6: Clean up and free allocated resources
    pimFree(a0Pim);
    pimFree(a1Pim);
    pimFree(b0Pim);
    pimFree(b1Pim);
    pimFree(cinPim);
    pimFree(sum0Pim);
    pimFree(sum1Pim);
    pimFree(coutPim);
    pimDeleteDevice();

    return 0;
}

