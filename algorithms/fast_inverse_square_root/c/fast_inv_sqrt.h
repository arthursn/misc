#ifndef FAST_INV_SQRT_H
#define FAST_INV_SQRT_H

#include <stdint.h>

float fast_inv_sqrt(float x)
{
    float xHalf = x * 0.5F;
    union {
        uint32_t bits;
        float value;
    } conv = { .value = x };
    conv.bits = 0x5f3759df - (conv.bits >> 1);
    conv.value = conv.value * (1.5F - (xHalf * conv.value * conv.value));
    return conv.value;
}

#endif