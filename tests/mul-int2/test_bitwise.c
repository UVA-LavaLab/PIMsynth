// Test bit-wise C code for mul-int2
// Use gcc to compile this with a .bitwise.c file
#include <stdio.h>

extern void func(int*, int*, int*, int*, int*, int*);

void main()
{
  for (int a1 = 0; a1 < 2; a1++) {
    for (int a0 = 0; a0 < 2; a0++) {
      for (int b1 = 0; b1 < 2; b1++) {
        for (int b0 = 0; b0 < 2; b0++) {
          int p0 = 0, p1 = 0;
          func(&a0, &a1, &b0, &b1, &p0, &p1);
          printf("%d %d  *  %d %d  =  %d %d\n", a1, a0, b1, b0, p1, p0);
        }
      }
    }
  }
}

