from ctypes import Union, c_double, c_float, c_uint32, c_uint64
from typing import Literal


class FastInverseSqrt:
    """
    Implementation of the Fast Inverse Square Root algorithm.

    This class implements the famous "Fast Inverse Square Root" algorithm
    originally from Quake III Arena, with configurable precision and iterations.

    Args:
        float_type: Type of floating point to use ("float" or "double")
        correction: Magic number correction factor
        newton_iterations: Number of Newton-Raphson iterations to perform
                          (more iterations = more accuracy, less speed)
    """

    def __init__(
        self,
        float_type: Literal["float", "double"] = "float",
        correction: float = 0.0450465,
        newton_iterations: int = 1,
    ):
        if float_type == "float":
            self.n_man, self.n_exp, c_float_type, c_uint_type = (
                23,
                8,
                c_float,
                c_uint32,
            )
        elif float_type == "double":
            self.n_man, self.n_exp, c_float_type, c_uint_type = (
                52,
                11,
                c_double,
                c_uint64,
            )
        else:
            raise ValueError(f"Unrecognized float_type {float_type}")

        class DynamicConverter(Union):
            _fields_ = [
                ("value", c_float_type),
                ("bits", c_uint_type),
            ]

        self.Converter = DynamicConverter
        self.correction = correction
        self.newton_iterations = newton_iterations
        self.wtf: int = self.compute_wtf()

    def compute_wtf(self) -> int:
        """
        Compute the "magic number" used in the fast inverse square root algorithm.

        The magic number depends on the floating point format (float/double) and
        the correction factor.

        Returns:
            int: The magic number constant
        """
        return int(
            3
            * (
                (1 << (self.n_man + self.n_exp - 2))
                - (1.0 + self.correction) * (1 << (self.n_man - 1))
            )
        )

    def inv_sqrt(self, x: float) -> float:
        """
        Calculate the inverse square root (1/√x) using the fast algorithm.

        This method uses bit manipulation and Newton-Raphson iterations to
        quickly approximate 1/√x.

        Args:
            x: The input value (must be positive)
        Returns:
            float: The approximate value of 1/√x
        """
        conv = self.Converter()
        conv.value = x
        x_half = x * 0.5
        conv.bits = self.wtf - (conv.bits >> 1)
        for _ in range(self.newton_iterations):
            conv.value = conv.value * (1.5 - (x_half * conv.value * conv.value))
        return conv.value
