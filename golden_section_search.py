# https://en.wikipedia.org/wiki/Golden-section_search
import math

GR = (math.sqrt(5) + 1) / 2  # Golden ratio


def gss(f, a, b, tol=1e-5):
    c = b - (b - a) / GR
    d = a + (b - a) / GR
    while abs(b - a) > tol:
        if f(c) > f(d):
            b = d
        else:
            a = c
        c = b - (b - a) / GR
        d = a + (b - a) / GR
    return (b + a) / 2


if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt

    def f(x):
        return np.sin(x)

    a, b = 0., 6.
    xmax = gss(f, a, b)

    fig, ax = plt.subplots()
    x = np.linspace(a, b, 100)
    ax.plot(x, f(x), 'k-')
    ax.plot([xmax], [f(xmax)], 'rx')
    ax.text(xmax*1.05, f(xmax), r'$x_{{max}} = {:g}$'.format(xmax))
    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')
    ax.set_title('Golden-section search algorithm')

    plt.show()
