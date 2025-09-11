#include "fast_inv_sqrt.h"
#include <math.h>
#include <stdio.h>

int main()
{
    float num = 5.0;
    printf("%g %g\n", 1 / sqrt(num), fast_inv_sqrt(num));
    return 0;
}