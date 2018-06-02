import numpy as np


def ulam_spiral_coords(N, origin=1):
    N = np.array(N)
    N -= origin - 1
    N = N[N >= 1]

    I, J = np.ndarray(N.shape), np.ndarray(N.shape)

    K = np.floor(N**.5)
    R = K % 2
    D = N - K**2

    crit1 = R == 0
    crit2 = D != 0
    crit3 = D <= K

    sel = crit1
    I[sel] = 1 - K[sel]/2
    J[sel] = K[sel]/2

    sel = ~crit1
    I[sel] = (K[sel] - 1)/2
    J[sel] = -(K[sel] - 1)/2

    sel = crit2 & crit3
    I[sel] -= (-1)**R[sel]
    J[sel] -= (D[sel] - 1)*(-1)**R[sel]

    sel = crit2 & ~crit3
    I[sel] -= (2 + K[sel] - D[sel])*(-1)**R[sel]
    J[sel] -= K[sel]*(-1)**R[sel]

    return I, J


import matplotlib.pyplot as plt


def get_primes(n):
    numbers = set(range(n, 1, -1))
    primes = []
    while numbers:
        p = numbers.pop()
        primes.append(p)
        numbers.difference_update(set(range(p*2, n+1, p)))
    return sorted(primes)


n = 200*200
origin = 1

p = get_primes(n + origin)

fig, ax = plt.subplots()
ax.plot(*ulam_spiral_coords(range(origin, n + origin), origin), 'r-', lw=.5)
ax.plot(*ulam_spiral_coords(p, origin), 'k.', ms=1)
ax.set_aspect('equal')

nroot = n**.5/2 + 1
ax.set_xlim(-nroot, nroot)
ax.set_ylim(-nroot, nroot)
ax.axis('off')
fig.tight_layout()
# fig.savefig('ulam_spiral.pdf')
fig.show()
