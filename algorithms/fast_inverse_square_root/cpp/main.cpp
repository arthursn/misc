#include "fast_inv_sqrt.hpp"
#include <print>

int main()
{
    std::println("{}", fast_inv_sqrt<float>(3.0));
    std::println("{}", fast_inv_sqrt<double>(3.0));
    return 0;
}