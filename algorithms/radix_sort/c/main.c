#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

size_t g_radixSizeBytes = 1;

typedef enum {
    RADIX_SUCCESS = 0,
    RADIX_NULL_POINTER,
    RADIX_MEMORY_ERROR,
    RADIX_INVALID_RADIX_SIZE,
} RadixSortError;

typedef struct Bucket {
    char* elements;
    size_t count;
    size_t size;
} Bucket;

RadixSortError addElementToBucket(Bucket* bucket, char* element, size_t width, size_t minBucketSize)
{
    if (bucket->elements == NULL) {
        bucket->size = minBucketSize;
        bucket->elements = malloc(width * bucket->size);
        if (bucket->elements == NULL) {
            return RADIX_MEMORY_ERROR;
        }
#ifdef DEBUG
        fprintf(stderr, "malloc called %p\n", bucket->elements);
#endif
    }
    if (bucket->count >= bucket->size) {
        bucket->size *= 2;
        void* previous = bucket->elements;
        bucket->elements = realloc(bucket->elements, width * bucket->size);
        if (bucket->elements == NULL) {
            return RADIX_MEMORY_ERROR;
        }
#ifdef DEBUG
        fprintf(stderr, "realloc called %p -> %p\n", previous, bucket->elements);
#endif
    }
    memcpy(bucket->elements + bucket->count * width, element, width);
    bucket->count++;

    return RADIX_SUCCESS;
}

void freeBucketElements(Bucket* bucket)
{
    free(bucket->elements);
    bucket->size = 0;
    bucket->count = 0;
}

RadixSortError radixSort(void* array, size_t len, size_t width)
{
    if (g_radixSizeBytes > sizeof(uintmax_t)) {
        return RADIX_INVALID_RADIX_SIZE;
    }

    if (array == NULL) {
        return RADIX_NULL_POINTER;
    }

    if (len <= 1) {
        return RADIX_SUCCESS;
    }

    const size_t numBuckets = 1 << (8 * g_radixSizeBytes);
    const size_t minBucketSize = len / numBuckets + 1;
    RadixSortError error;
    Bucket* buckets = malloc(numBuckets * sizeof(Bucket));
    memset(buckets, 0, numBuckets * sizeof(Bucket));

    char significantBits = 0;
    int mostSignificantByte = width - 1;
    while (mostSignificantByte >= 0) {
        for (size_t arrayIndex = 0; arrayIndex < len; arrayIndex++) {
            significantBits |= *((char*)array + arrayIndex * width + mostSignificantByte);
        }
        if (significantBits) {
            break;
        }
        mostSignificantByte--;
    }

    for (size_t byteIndex = 0; byteIndex <= mostSignificantByte; byteIndex += g_radixSizeBytes) {
        // Zeroes bucket count
        for (size_t bucketIndex = 0; bucketIndex < numBuckets; bucketIndex++) {
            buckets[bucketIndex].count = 0;
        }

        // Loop over all elements of array
        for (size_t arrayIndex = 0; arrayIndex < len; arrayIndex++) {
            char* element = array + arrayIndex * width; // element as char array
            uintmax_t bucketIndex = 0; // bucket index (must be sized at least g_radixSizeBytes)
            size_t byteIndexTmp = byteIndex;
            for (size_t subElementIndex = 0; subElementIndex < g_radixSizeBytes; subElementIndex++) {
                // Copy single byte (1 char element) to bucket index
                memcpy(&bucketIndex + subElementIndex, element + byteIndexTmp++, 1);
            }
            // Place the numbers into their corresponding buckets
            error = addElementToBucket(buckets + bucketIndex, element, width, minBucketSize);
            if (error != RADIX_SUCCESS) {
                return error;
            }
        }

        // Unpack elements in the buckets to array
        size_t bytePosition = 0;
        for (size_t bucketIndex = 0; bucketIndex < numBuckets; bucketIndex++) {
            Bucket* bucket = buckets + bucketIndex;
            if (bucket->count > 0) {
                size_t byteShift = bucket->count * width;
                memcpy(array + bytePosition, buckets[bucketIndex].elements, byteShift);
                bytePosition += byteShift;
            }
        }
    }

    // Free memory
    for (size_t bucketIndex = 0; bucketIndex < numBuckets; bucketIndex++) {
        freeBucketElements(buckets + bucketIndex);
    }
    free(buckets);

    return RADIX_SUCCESS;
}

int main()
{
#define TYPE int64_t
#define FMT "%ld "
    // This is inneficient; there are too many buckets
    g_radixSizeBytes = 2;
    TYPE array[] = { 4.13, 1.34, 33 << 4, 0, 10.1, 3e4, 104.34, 1.0, 2.57, 53, 1025, 1 << 10 };
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