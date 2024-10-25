#include <iostream>
#include <cstdlib>
#include <ctime>
#include <cassert>
#include <cstring>
#include "tmp.hpp"
#include "libpimeval.h"

// Golden model function
void funcGoldenModel(
   int a,
   int b,
   int cin,
   int& cout,
   int& sum
) {
   cout = (a + b + cin) / 2;
   sum = (a + b + cin) % 2;
}

void runTest(int testNumber, PimObjId aPim, PimObjId bPim, PimObjId cinPim, PimObjId sumPim, PimObjId coutPim) {
    // Generate random input values
    int a = std::rand() % 2;
    int b = std::rand() % 2;
    int cin = std::rand() % 2;
    int sum, cout;

    std::cout << "Info: Test " << testNumber << ": a = " << a << ", b = " << b << ", cin = " << cin << std::endl;

    // Calculate golden model results
    funcGoldenModel(a, b, cin, cout, sum);

    // Copy data to PIM device
    pimCopyHostToDevice(&a, aPim);
    pimCopyHostToDevice(&b, bPim);
    pimCopyHostToDevice(&cin, cinPim);

    // Call the function under test
    func(aPim, bPim, cinPim, coutPim, sumPim);

    // Retrieve results and compare
    int pimSum, pimCout;
    pimCopyDeviceToHost(sumPim, &pimSum);
    pimCopyDeviceToHost(coutPim, &pimCout);

    // Assert that the PIM output matches the golden model output
    assert(pimSum == sum && pimCout == cout);

    if (pimSum == sum && pimCout == cout) {
        std::cout << "Info: Test " << testNumber << " passed!" << std::endl;
    } else {
        std::cerr << "Error: Test " << testNumber << " failed!" << std::endl;
        std::cerr << "Expected sum: " << sum << ", PIM sum: " << pimSum << std::endl;
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
    PimObjId aPim = pimAlloc(PIM_ALLOC_V, 1, PIM_INT32);
    PimObjId bPim = pimAllocAssociated(aPim, PIM_INT32);
    PimObjId cinPim = pimAllocAssociated(aPim, PIM_INT32);
    PimObjId sumPim = pimAllocAssociated(aPim, PIM_INT32);
    PimObjId coutPim = pimAllocAssociated(aPim, PIM_INT32);

    // Step 5: Run the configurable number of test cases
    for (int i = 0; i < testCount; ++i) {
        runTest(i + 1, aPim, bPim, cinPim, sumPim, coutPim);
    }

    // Step 6: Clean up and free allocated resources
    pimFree(aPim);
    pimFree(bPim);
    pimFree(cinPim);
    pimFree(sumPim);
    pimFree(coutPim);
    pimDeleteDevice();

    return 0;
}

