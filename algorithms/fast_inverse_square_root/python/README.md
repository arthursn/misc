# Fast Inverse Square Root

Python implementation of the famous "Fast Inverse Square Root" algorithm from Quake III Arena.

## Features

- Supports both float and double precision
- Configurable Newton-Raphson iterations
- Correction factor optimization

## Usage

```python
from fast_inv_sqrt import FastInverseSqrt

# Basic usage
fisqrt = FastInverseSqrt(float_type="float")
result = fisqrt.inv_sqrt(4.0)  # ≈ 0.5

# Advanced usage
fisqrt = FastInverseSqrt(
    float_type="double",
    correction=0.045,
    newton_iterations=2
)
```

## Optimization

```python
from main import optimize_correction

# Find optimal correction factor
optimal_correction, error = optimize_correction(
    float_type="float",
    test_range=(1, 100)
)
```
