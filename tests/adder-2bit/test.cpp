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

// Test runner function
void runTest(int testNumber, PimObjId a, PimObjId b, PimObjId cin, PimObjId cout, PimObjId sum) {
    // Generate random input values
    int a0 = std::rand() % 2;
    int a1 = std::rand() % 2;
    int b0 = std::rand() % 2;
    int b1 = std::rand() % 2;
    int cinVal = std::rand() % 2;
    int sum0, sum1, coutVal;

    std::cout << "Info: Test " << testNumber << ": a0 = " << a0 << ", a1 = " << a1 
              << ", b0 = " << b0 << ", b1 = " << b1 << ", cin = " << cinVal << std::endl;

    // Calculate golden model results
    funcGoldenModel(a0, a1, b0, b1, cinVal, coutVal, sum0, sum1);

    // Pack the inputs into 2-bit integers
    int aVal = (a0 << 0) | (a1 << 1);
    int bVal = (b0 << 0) | (b1 << 1);

    // Copy data to PIM device
    pimCopyHostToDevice(&aVal, a);
    pimCopyHostToDevice(&bVal, b);
    pimCopyHostToDevice(&cinVal, cin);

    // Call the function under test
    func(a, b, cin, cout, sum);

    // Retrieve results and compare
    int pimSum, pimCout;
    pimCopyDeviceToHost(sum, &pimSum);
    pimCopyDeviceToHost(cout, &pimCout);

    int pimSum0 = pimSum & 1;
    int pimSum1 = (pimSum >> 1) & 1;

    if (pimSum0 == sum0 && pimSum1 == sum1 && pimCout == coutVal) {
        std::cout << "Info: Test " << testNumber << " passed!" << std::endl;
    } else {
        std::cerr << "Error: Test " << testNumber << " failed!" << std::endl;
        std::cerr << "Expected sum0: " << sum0 << ", PIM sum0: " << pimSum0 << std::endl;
        std::cerr << "Expected sum1: " << sum1 << ", PIM sum1: " << pimSum1 << std::endl;
        std::cerr << "Expected cout: " << coutVal << ", PIM cout: " << pimCout << std::endl;
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
    // Specify element size as 1 and data type as PIM_INT32
    PimObjId a = pimAlloc(PIM_ALLOC_V, 1, PIM_INT32);  // 2-bit input
    PimObjId b = pimAllocAssociated(a, PIM_INT32);    // 2-bit input
    PimObjId cin = pimAllocAssociated(a, PIM_INT32);  // 1-bit input
    PimObjId cout = pimAllocAssociated(a, PIM_INT32); // 1-bit output
    PimObjId sum = pimAllocAssociated(a, PIM_INT32);  // 2-bit output

    // Step 5: Run the configurable number of test cases
    for (int i = 0; i < testCount; ++i) {
        runTest(i + 1, a, b, cin, cout, sum);
    }

    // Step 6: Clean up and free allocated resources
    pimFree(a);
    pimFree(b);
    pimFree(cin);
    pimFree(cout);
    pimFree(sum);
    pimDeleteDevice();

    return 0;
}

