#!/usr/bin/python3

import time
import numpy as np
import matplotlib.pyplot as plt


class Mandelbrot(object):
    def __init__(self, size=1024, maxit=100, horizon=2.):
        self.size = size
        self.maxit = maxit
        self.horizon = horizon

    def compute(self, realrng=[-2, .5], imagrng=[-1.25, 1.25]):
        imin, imax = imagrng   # y-axis, rows
        rmin, rmax = realrng   # x-axis, columns
        step = max((imax-imin)/(self.size-1), (rmax-rmin)/(self.size-1))

        I, R = np.mgrid[imin:imax:step, rmin:rmax:step]
        C = R + I*1.j
        Z = np.zeros(C.shape, dtype=np.complex)
        N = np.zeros(C.shape, dtype=int)    # number of iterations

        for it in range(self.maxit):
            sel = abs(Z) <= self.horizon
            Z[sel] = Z[sel]**2. + C[sel]
            N[sel] = it + 1

        return N

    def budhabrot(self, realrng=[-2, 2], imagrng=[-2, 2], bins=[512, 512]):
        imin, imax = imagrng   # y-axis, rows
        rmin, rmax = realrng   # x-axis, columns
        step = max((imax-imin)/(self.size-1), (rmax-rmin)/(self.size-1))

        I, R = np.mgrid[imin:imax:step, rmin:rmax:step]
        C = R + I*1.j
        Z = np.zeros(C.shape, dtype=np.complex)
        P = np.ndarray((self.maxit,) + C.shape, dtype=np.complex)
        P.fill(np.nan)

        for it in range(self.maxit):
            sel = abs(Z) <= self.horizon
            P[it][sel] = Z[sel]
            Z[sel] = Z[sel]**2. + C[sel]

        P = P.ravel()
        P = P[np.logical_not(np.isnan(P))]

        return np.histogram2d(P.imag, P.real, bins=bins)


def onrescale(ax):
    ax.set_autoscale_on(False)

    fig = ax.figure
    img = ax.images[-1]

    x, y, dx, dy = ax.viewLim.bounds
    realrng = [x, x + dx]
    imagrng = [y, y + dy]

    # print(realrng, imagrng)
    N = mset.compute(realrng, imagrng)

    img.set_data(N)
    img.set_extent(realrng + imagrng)

    fig.canvas.draw_idle()


mset = Mandelbrot(size=1024, maxit=50)
N = mset.compute()

fig1, ax1 = plt.subplots()
ax1.imshow(N, origin='lower', extent=(-2, .5, -1.25, 1.25))
ax1.callbacks.connect('xlim_changed', onrescale)
ax1.callbacks.connect('ylim_changed', onrescale)

# # budhabrot
# mset = Mandelbrot(size=1024, maxit=100)
# H, X, Y = mset.budhabrot(bins=(1024,1024))

# fig2, ax2 = plt.subplots()
# ax2.imshow(np.log(H), extent=(X.min(), X.max(), Y.min(), Y.max()))

plt.show()
