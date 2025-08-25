#include "radix_sort.h"
#include <stdio.h>

int main()
{
#define TYPE float
#define FMT "%g "
    g_radixSizeBytes = 2; // This is inneficient; there are too many buckets
    TYPE array[] = { 4.13, 1.34, 33 << 10, 0, 10.1, 3e4, 104.34, 1.0, 2.57, 53, 1025, 1 << 3 };
    // TYPE array[] = "H3110 w0r1d?!";

    size_t len = sizeof(array) / sizeof(TYPE);

    for (size_t arrayIndex = 0; arrayIndex < len; arrayIndex++) {
        printf(FMT, array[arrayIndex]);
    }
    printf("\n");

    radixSort(array, len, sizeof(TYPE));

    for (size_t arrayIndex = 0; arrayIndex < len; arrayIndex++) {
        printf(FMT, array[arrayIndex]);
    }
    printf("\n");

    return 0;
}