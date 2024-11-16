#include <iostream>
#include <cstdlib>
#include <ctime>
#include "tmp.hpp"
#include "libpimeval.h"

// 32-bit golden model function (without cout)
void funcGoldenModel(
    int a[32], 
    int b[32], 
    int sum[32]
) {
    int carry = 0;
    for (int i = 0; i < 32; ++i) {
        int partial_sum = a[i] + b[i] + carry;
        sum[i] = partial_sum % 2;
        carry = partial_sum / 2;
    }
}

void runTest(int testNumber, int a[32], int b[32], PimObjId aPim[32], PimObjId bPim[32], PimObjId sumPim[32]) {
    // Calculate expected results using the golden model
    int sum[32];
    funcGoldenModel(a, b, sum);

    // Copy data to PIM device
    for (int i = 0; i < 32; ++i) {
        pimCopyHostToDevice(&a[i], aPim[i]);
        pimCopyHostToDevice(&b[i], bPim[i]);
    }

    // Call the function under test
    func(
        aPim[0], aPim[1], aPim[2], aPim[3], aPim[4], aPim[5], aPim[6], aPim[7],
        aPim[8], aPim[9], aPim[10], aPim[11], aPim[12], aPim[13], aPim[14], aPim[15],
        aPim[16], aPim[17], aPim[18], aPim[19], aPim[20], aPim[21], aPim[22], aPim[23],
        aPim[24], aPim[25], aPim[26], aPim[27], aPim[28], aPim[29], aPim[30], aPim[31],
        bPim[0], bPim[1], bPim[2], bPim[3], bPim[4], bPim[5], bPim[6], bPim[7],
        bPim[8], bPim[9], bPim[10], bPim[11], bPim[12], bPim[13], bPim[14], bPim[15],
        bPim[16], bPim[17], bPim[18], bPim[19], bPim[20], bPim[21], bPim[22], bPim[23],
        bPim[24], bPim[25], bPim[26], bPim[27], bPim[28], bPim[29], bPim[30], bPim[31],
        sumPim[0], sumPim[1], sumPim[2], sumPim[3], sumPim[4], sumPim[5], sumPim[6], sumPim[7],
        sumPim[8], sumPim[9], sumPim[10], sumPim[11], sumPim[12], sumPim[13], sumPim[14], sumPim[15],
        sumPim[16], sumPim[17], sumPim[18], sumPim[19], sumPim[20], sumPim[21], sumPim[22], sumPim[23],
        sumPim[24], sumPim[25], sumPim[26], sumPim[27], sumPim[28], sumPim[29], sumPim[30], sumPim[31]
    );

    // Retrieve and verify the results from the PIM device
    int pimSum[32];
    for (int i = 0; i < 32; ++i) {
        pimCopyDeviceToHost(sumPim[i], &pimSum[i]);
    }

    // Check if the test passed and print mismatch details if it failed
    bool testPassed = true;
    for (int i = 0; i < 32; ++i) {
        if (pimSum[i] != sum[i]) {
            testPassed = false;
            break;
        }
    }

    if (!testPassed) {
        // Print all inputs and outputs if there is a mismatch
        std::cerr << "Error: Test " << testNumber << " failed!" << std::endl;

        // Print input values in MSB to LSB order
        std::cerr << "Input values: " << std::endl;
        std::cerr << "  a = [ ";
        for (int i = 31; i >= 0; --i) std::cerr << a[i] << " ";
        std::cerr << "], b = [ ";
        for (int i = 31; i >= 0; --i) std::cerr << b[i] << " ";
        std::cerr << "]" << std::endl;

        // Print expected output in MSB to LSB order
        std::cerr << "Expected Output:" << std::endl;
        std::cerr << "  sum = [ ";
        for (int i = 31; i >= 0; --i) std::cerr << sum[i] << " ";
        std::cerr << "]" << std::endl;

        // Print PIM output in MSB to LSB order
        std::cerr << "PIM Output:" << std::endl;
        std::cerr << "  sum = [ ";
        for (int i = 31; i >= 0; --i) std::cerr << pimSum[i] << " ";
        std::cerr << "]" << std::endl;
    } else {
        std::cout << "Info: Test " << testNumber << " passed!" << std::endl;
    }
}

void intToBinaryArray(int value, int arr[32]) {
    for (int i = 0; i < 32; ++i) {
        arr[i] = (value >> i) & 1;
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

    // Allocate PIM objects for the 32-bit input/output ports
    PimObjId aPim[32], bPim[32], sumPim[32];
    for (int i = 0; i < 32; ++i) {
        aPim[i] = pimAlloc(PIM_ALLOC_V, 1, PIM_INT32);
        bPim[i] = pimAllocAssociated(aPim[i], PIM_INT32);
        sumPim[i] = pimAllocAssociated(aPim[i], PIM_INT32);
    }

    // Run random tests
    int testNumber = 1;
    int numTests = 100;  // Number of random test cases
    for (int t = 0; t < numTests; ++t) {
        unsigned int a_val = std::rand();  // Generate random 32-bit value for a
        unsigned int b_val = std::rand();  // Generate random 32-bit value for b

        int a[32], b[32];
        intToBinaryArray(a_val, a);  // Convert integer a_val to 32-bit binary array
        intToBinaryArray(b_val, b);  // Convert integer b_val to 32-bit binary array

        runTest(testNumber++, a, b, aPim, bPim, sumPim);
    }

    // Clean up and free allocated resources
    for (int i = 0; i < 32; ++i) {
        pimFree(aPim[i]);
        pimFree(bPim[i]);
        pimFree(sumPim[i]);
    }
    pimDeleteDevice();

    return 0;
}

