#ifndef UTILS_H
#define UTILS_H 
#include "libpimeval.h"
#include <iostream> 
#include <vector>

int64_t getPimRegisterValue(PimRowReg reg) {
  // Step 1: Allocate a temporary PIM object
  PimObjId tempObj = pimAlloc(PIM_ALLOC_V, 1, PIM_INT64);

  // Step 2: Allocate a temporary vector
  int64_t* tempVector = new int64_t[1];

  // Step 3: Move the PIM row register to the PIM temporary object using PIM_RREG_SA
  pimOpMove(tempObj, reg, PIM_RREG_SA);  // Move the register to PIM_RREG_SA

  // Write from the SA register to the PIM row in tempObj
  pimOpWriteSaToRow(tempObj, 0); // Write SA contents to the first row of tempObj

  // Step 4: Copy the PIM temporary object to the temporary vector
  pimCopyDeviceToHost(tempObj, tempVector, 0, 1);

  // Step 5: Retrieve the first element of the vector
  int64_t registerValue = tempVector[0];

  // Step 6: Free the temporary vector
  delete[] tempVector;

  // Step 7: Free the PIM object
  pimFree(tempObj);

  // Return the register value
  return registerValue;
}


#endif 
