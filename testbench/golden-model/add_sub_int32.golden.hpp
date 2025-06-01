#ifndef ADD_SUB_INT32_GOLDEN
#define ADD_SUB_INT32_GOLDEN 
#include <stdlib.h>
// SIGNATURE_START
void add_sub_int32_golden(uint32_t  a, uint32_t b, uint32_t c, uint8_t* y) 
// SIGNATURE_END
{
    *y = a + b - c;
    return; 
}

#endif
