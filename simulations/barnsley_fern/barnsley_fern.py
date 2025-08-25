from abc import ABC
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes


class Transformation(ABC):
    A: npt.NDArray
    B: npt.NDArray

    # Linear transformations applied to coordinates
    def __call__(self, *xy):
        return self.A.dot(xy) + self.B


class F1(Transformation):
    A = np.array([[0, 0], [0, 0.16]])
    B = np.array([0, 0])


class F2(Transformation):
    A = np.array([[0.85, 0.04], [-0.04, 0.85]])
    B = np.array([0, 1.60])


class F3(Transformation):
    A = np.array([[0.20, -0.26], [0.23, 0.22]])
    B = np.array([0, 1.60])


class F4(Transformation):
    A = np.array([[-0.15, 0.28], [0.26, 0.24]])
    B = np.array([0, 0.44])


class BarnsleyFern:
    def __init__(self):
        # Instantiate the four possible transformations
        self.f: List[Transformation] = [F1(), F2(), F3(), F4()]
        # Probabilities assigned to each transformation
        self.p: List[float] = [0.01, 0.85, 0.07, 0.07]
        # Coordinates as list
        self._xy: List[Tuple[int, int]] = [(0, 0)]

    @property
    def xy(self) -> npt.NDArray:
        # Coordinates as numpy array
        return np.array(self._xy)

    def iteration(self) -> None:
        # Choose one of the four transformations based on the probabilies
        # and apply it to last point
        self._xy.append(np.random.choice(self.f, p=self.p)(*self._xy[-1]))  # type: ignore

    def generate(self, niter: int) -> None:
        for _ in range(niter):
            self.iteration()

    def plot(self, ax: Optional[Axes] = None, **kwargs) -> Axes:
        # Plot using ax.plot
        if ax is None:
            fig, ax = plt.subplots(figsize=(4.5, 7))
        ax.axis("off")
        ax.axis("equal")
        # Default plot settings
        _kwargs = dict(marker="x", ls="none", ms=0.2, c="g")
        _kwargs.update(kwargs)
        ax.plot(*self.xy.T, **_kwargs)  # type: ignore
        return ax

    def scatter(self, ax: Optional[Axes] = None, **kwargs) -> Axes:
        # Plot using ax.scatter (it's possible to plot with colors)
        if ax is None:
            fig, ax = plt.subplots(figsize=(4.5, 7))
        ax.axis("off")
        ax.axis("equal")
        # By default, use as color code the iteration step corresponding
        # to the generation of a given point
        kw = dict(marker="x", s=0.2, c=range(len(self._xy)))
        kw.update(kwargs)
        ax.scatter(*self.xy.T, **kw)
        return ax


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--niter",
        type=lambda x: int(float(x)),
        help="Number of iterations",
        default=int(1e5),
    )
    parser.add_argument(
        "-c",
        "--color",
        help="If true, plot with a colormap representing the iteration step for each point",
        action="store_true",
    )
    args = parser.parse_args()

    fern = BarnsleyFern()
    fern.generate(args.niter)

    if args.color:
        fern.scatter()
    else:
        fern.plot()

    plt.show()
