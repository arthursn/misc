#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt


class Mandelbrot(object):
    def __init__(self, size=1024, maxit=100, horizon=2.):
        self.size = size
        self.maxit = maxit
        self.horizon = horizon

    def compute(self, realrng=[-2, .5], imagrng=[-1.25, 1.25]):
        real, imag = np.meshgrid(np.linspace(*realrng, self.size),
                                 np.linspace(*imagrng, self.size))

        C = real + imag*1.j
        Z = np.zeros(C.shape, dtype=np.complex)
        N = np.zeros(C.shape, dtype=int)  # number of iterations

        for it in range(self.maxit):
            sel = abs(Z) <= self.horizon
            Z[sel] = Z[sel]**2. + C[sel]
            N[sel] = it + 1

        return N


def onrescale(ax):
    ax.set_autoscale_on(False)

    fig = ax.figure
    img = ax.images[-1]

    x, y, dx, dy = ax.viewLim.bounds
    realrng = [x, x + dx]
    imagrng = [y, y + dy]

    N = mset.compute(realrng, imagrng)

    img.set_data(N)
    img.set_extent(realrng + imagrng)

    fig.canvas.draw_idle()


if __name__ == '__main__':
    mset = Mandelbrot(size=1024, maxit=50)
    N = mset.compute()

    fig1, ax1 = plt.subplots()
    ax1.imshow(N, origin='lower', extent=(-2, .5, -1.25, 1.25))
    ax1.callbacks.connect('xlim_changed', onrescale)
    ax1.callbacks.connect('ylim_changed', onrescale)

    plt.show()
