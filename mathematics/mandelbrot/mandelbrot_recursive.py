import numpy as np
import matplotlib.pyplot as plt


def f(c, maxit, z=0, it=0):
    """
    Recursive Mandelbrot
    """
    if abs(z) <= 2. and it < maxit:
        return f(c, maxit, z**2. + c, it + 1)
    else:
        return it


if __name__ == '__main__':
    realrng = [-2, .75]
    imagrng = [-1.5, 1.5]
    size = 512
    maxit = 100

    # real and imag parts grid
    real, imag = np.meshgrid(np.linspace(*realrng, size),
                             np.linspace(*imagrng, size))

    # c values
    c_set = real + imag*1.j
    c_shape = c_set.shape

    its = []
    for c in c_set.ravel():
        its.append(f(c, maxit))

    its = np.array(its).reshape(c_shape)

    fig, ax = plt.subplots()
    ax.pcolormesh(real, imag, its)
    ax.set_aspect('equal')

    plt.show()
