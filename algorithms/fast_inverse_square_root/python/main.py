from typing import Any, Dict, Sequence

import numpy as np
from fast_inv_sqrt import FastInverseSqrt
from scipy import optimize


def optimize_correction(
    model_kwargs: Dict[str, Any],
    test_values: Sequence[float] = np.logspace(-1, 2, 1000),  # type: ignore
    minimize_kwargs: Dict[str, Any] = dict(
        bounds=(-0.1, 0.1),
        method="bounded",
    ),
):
    # True inverse square root values
    true_values = 1.0 / np.sqrt(test_values)

    def error_function(correction):
        model = FastInverseSqrt(correction=correction, **model_kwargs)
        # Calculate fast inverse square root for all test values
        approx_values = np.array([model.inv_sqrt(float(x)) for x in test_values])
        # Calculate relative error
        rel_errors = ((approx_values - true_values) / true_values) ** 2
        # Return mean relative error
        return np.sqrt(np.mean(rel_errors))

    # Find the correction value that minimizes the error
    result = optimize.minimize_scalar(
        error_function,
        **minimize_kwargs,
    )

    optimal_correction = result.x
    min_error = result.fun

    return optimal_correction, min_error


def main():
    model_kwargs = dict(
        float_type="float",
        newton_iterations=1,
    )

    print("Reference")
    print(f" 1/sqrt(3) = {1 / np.sqrt(3)}")
    # Standard usage
    model_og = FastInverseSqrt(**model_kwargs)  # type: ignore
    print("Standard")
    print(f" 1/sqrt(3) ≈ {model_og.inv_sqrt(3)}")
    print(" correction:", model_og.correction)
    print(" WTF:", hex(model_og.wtf))

    optimal_corr, min_error = optimize_correction(
        model_kwargs=model_kwargs,
        test_values=np.linspace(1, 10, 100),  # type: ignore
        # test_values=[1, 4, 16, 64, 256, 1024],
    )

    model_opt = FastInverseSqrt(
        correction=optimal_corr,
        **model_kwargs,  # type: ignore
    )
    print("Optimized")
    print(f" 1/sqrt(3) ≈ {model_opt.inv_sqrt(3)}")
    print(" correction:", model_opt.correction)
    print(" WTF:", hex(model_opt.wtf))


if __name__ == "__main__":
    main()
