from ctypes import Union, c_double, c_float, c_uint32, c_uint64
from typing import Literal


class FastInverseSqrt:
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
        return int(
            3
            * (
                (1 << (self.n_man + self.n_exp - 2))
                - (1.0 + self.correction) * (1 << (self.n_man - 1))
            )
        )

    def isqrt(self, x: float) -> float:
        conv = self.Converter()
        conv.value = x
        x_half = x * 0.5
        conv.bits = self.wtf - (conv.bits >> 1)
        for _ in range(self.newton_iterations):
            conv.value = conv.value * (1.5 - (x_half * conv.value * conv.value))
        return conv.value
