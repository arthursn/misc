#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt


class Transformation:
    # Linear transformations applied to coordinates
    def __call__(self, *xy):
        return self.A.dot(xy) + self.B


class F1(Transformation):
    A = np.array([[0,   0],
                  [0, 0.16]])
    B = np.array([0,  0])


class F2(Transformation):
    A = np.array([[0.85, 0.04],
                  [-0.04, 0.85]])
    B = np.array([0, 1.60])


class F3(Transformation):
    A = np.array([[0.20, -0.26],
                  [0.23, 0.22]])
    B = np.array([0, 1.60])


class F4(Transformation):
    A = np.array([[-0.15, 0.28],
                  [0.26, 0.24]])
    B = np.array([0, 0.44])


class BarnsleyFern:
    def __init__(self):
        # Instantiate the four possible transformations
        self.f = [F1(), F2(), F3(), F4()]
        # Probabilities assigned to each transformation
        self.p = [0.01, 0.85, 0.07, 0.07]
        # Coordinates as list
        self._xy = [[0, 0]]

    @property
    def xy(self):
        # Coordinates as numpy array
        return np.array(self._xy)

    def iteration(self):
        # Choose one of the four transformations based on the probabilies
        # and apply it to last point
        self._xy.append(np.random.choice(self.f, p=self.p)(*self._xy[-1]))

    def generate(self, niterations):
        for n in range(int(niterations)):
            self.iteration()

    def plot(self, ax=None, **kwargs):
        # Plot using ax.plot
        if ax is None:
            fig, ax = plt.subplots(figsize=(4.5, 7))
        ax.axis('off')
        ax.axis('equal')
        # Default plot settings
        kw = dict(marker='x', ls='none', ms=.2, c='g')
        kw.update(kwargs)
        ax.plot(*self.xy.T, **kw)
        return ax

    def scatter(self, ax=None, **kwargs):
        # Plot using ax.scatter (it's possible to plot with colors)
        if ax is None:
            fig, ax = plt.subplots(figsize=(4.5, 7))
        ax.axis('off')
        ax.axis('equal')
        # By default, use as color code the iteration step corresponding
        # to the generation of a given point
        kw = dict(marker='x', s=.2, c=range(len(self._xy)))
        kw.update(kwargs)
        ax.scatter(*self.xy.T, **kw)
        return ax


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--niterations', type=lambda x: int(float(x)), default=int(1e5))
    parser.add_argument('-c', '--color', action='store_true')
    args = parser.parse_args()

    fern = BarnsleyFern()
    fern.generate(args.niterations)

    if args.color:
        fern.scatter()
    else:
        fern.plot()

    plt.show()
