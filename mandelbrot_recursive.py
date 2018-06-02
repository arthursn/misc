import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector

def f(c, maxit, z=0, it=0):
    """
    Recursive Mandelbrot
    """
    if abs(z) <= 2. and it < maxit:
        return f(c, maxit, z**2. + c, it + 1)
    else:
        return it


fig, ax = plt.subplots()

realrng = [-2, .75]
imagrng = [-1.5, 1.5]
# realrng = [-.15, -.10]
# imagrng = [-1, -.975]
size = 512
maxit = 100

imin, imax = imagrng   # y-axis, rows
rmin, rmax = realrng   # x-axis, columns
step = max((imax-imin)/(size-1), (rmax-rmin)/(size-1))

imag, real = np.mgrid[imin:imax:step, rmin:rmax:step]
c_set = real + imag*1.j
c_shape = c_set.shape

its = []

t0 = time.time()

for c in c_set.ravel():
    its.append(f(c, maxit))

print(time.time() - t0)

its = np.array(its).reshape(c_shape)

ax.pcolormesh(real, imag, its)
ax.set_aspect('equal')

plt.show()

