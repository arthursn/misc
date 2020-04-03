import random
import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle


class ElementaryCA():
    __i, __j, __k = np.mgrid[:2, :2, :2]
    pattern_indices = 7 - __k - 2*__j - 4*__i

    def __init__(self, rule, size, time):
        self.rule = np.array([bool(int(v)) for v in format(rule, '08b')])
        if len(self.rule) != 8:
            raise Exception('rule={} is invalid. rule must be < 256'.format(rule))

        self.size = size
        self.time = time
        self.grid = np.full((self.time, self.size), False)

        self.pattern_map = self.rule[self.pattern_indices]

        self.fig, self.ax = None, None
        self.img = None

    def set_single_seed(self, j, v=True):
        """
        Sets value for single seed
        """
        self.grid[0, j] = v

    def generate_random_seed(self):
        """
        Generates random seed as string with length self.size
        """
        seed = format(random.getrandbits(self.size), '0{}b'.format(self.size))
        print('Random seed:', seed)
        return seed

    def set_seed(self, seed):
        """
        Sets seed provided as string with length self.size  
        """
        j, = np.where([bool(int(v)) for v in seed])
        self.grid[0, j] = True

    def init_random_seed(self):
        """
        Initializes random seed
        """
        seed = self.generate_random_seed()
        self.set_seed(seed)

    def run(self):
        """
        Runs cellular automaton
        """
        for t in range(1, self.time):
            for j in range(self.size):
                neighbors = self.grid[t-1, max(0, j-1):j+2].astype(int)
                # Periodic boundary condition
                if j == 0:
                    g1_ = self.grid[t-1, -1].astype(int)
                    g0, g1 = neighbors
                elif j == self.size - 1:
                    g1_, g0 = neighbors
                    g1 = self.grid[t-1, 0].astype(int)
                else:
                    g1_, g0, g1 = neighbors

                self.grid[t, j] = self.pattern_map[g1_, g0, g1]

    def plot(self, ax=None, **kwargs):
        """
        Plots cellular automaton
        """
        if ax is None:
            self.fig, self.ax = plt.subplots()
        else:
            self.ax = ax
            self.fig = self.ax.get_figure()
        self.img = self.ax.imshow(self.grid, **kwargs)
        return self.ax


def run_ca(rule, size, time, random=False, ax=None):
    ca = ElementaryCA(rule, size, time)
    title = 'Rule {}'.format(rule)
    if random:
        ca.init_random_seed()
        title += ' random seed'
    else:
        ca.set_single_seed(min(time, size-1))
    ca.run()
    if ax is None:
        fig, ax = plt.subplots()
    ca.plot(ax, cmap='gray_r')
    ax.axis('off')
    ax.set_title(title)
    return ca


def nice_examples(fout=None):
    size = 257
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    run_ca(30, size, size//2, False, axes[0, 0])  # rule 30
    run_ca(90, size, size//2, False, axes[0, 1])  # rule 90
    run_ca(110, size, size, False, axes[1, 0])  # rule 110
    run_ca(90, size, size, True, axes[1, 1])  # rule 90 random
    fig.tight_layout()
    if fout is not None:
        fig.savefig(fout, dpi=300)


def generate_all_ca(random=True, fout=None):
    size = 129
    time = size
    figsize = (30, 30)
    if not random:
        time //= 2
        figsize = (30, 20)
    fig, axes = plt.subplots(16, 16, figsize=figsize)
    cyaxes = cycle(axes.ravel())
    for i in range(256):
        ax = next(cyaxes)
        run_ca(i, size, time, random, ax)
        ax.set_title(str(i))
    fig.tight_layout()
    if fout is not None:
        fig.savefig(fout, dpi=300)


if __name__ == '__main__':
    nice_examples('examples.png')
    generate_all_ca(False, 'all_single_seed.png')
    generate_all_ca(True, 'all_random_seed.png')
    plt.close('all')
