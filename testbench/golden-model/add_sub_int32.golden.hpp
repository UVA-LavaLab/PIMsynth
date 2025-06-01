#ifndef ADD_SUB_INT32_GOLDEN
#define ADD_SUB_INT32_GOLDEN 
#include <stdlib.h>
// SIGNATURE_START
void add_sub_int32_golden(int32_t  a, int32_t b, int32_t c, int32_t* y)
// SIGNATURE_END
{
    *y = a + b - c;
    return; 
}

#endif
