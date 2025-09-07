#pragma once

#include <cstdint>

template <typename T>
struct BitEquivalent;

template <>
struct BitEquivalent<float> {
    using type = std::uint32_t;
};

template <>
struct BitEquivalent<double> {
    using type = std::uint64_t;
};

template <typename T>
using BitEquivalent_t = typename BitEquivalent<T>::type;

template <typename T>
union Converter {
    T value;
    BitEquivalent_t<T> bits;
};

template <typename T>
struct WTF;

template <>
struct WTF<float> {
    static inline constexpr BitEquivalent_t<float> value = 0x5f3580eb;
};

template <>
struct WTF<double> {
    static inline constexpr BitEquivalent_t<double> value = 0x5fe6b01866d70800;
};

template <typename T>
T fast_inv_sqrt(T x)
{
    T xHalf = x * 0.5F;
    Converter<T> conv { .value = x };
    conv.bits = WTF<T>::value - (conv.bits >> 1);
    conv.value = conv.value * (1.5F - (xHalf * conv.value * conv.value));
    return conv.value;
}