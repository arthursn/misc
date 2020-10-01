import numpy as np
import matplotlib.pyplot as plt


class Transformation:
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
        self.f = [F1(), F2(), F3(), F4()]
        self.p = [0.01, 0.85, 0.07, 0.07]
        self._xy = [[0, 0]]

    @property
    def xy(self):
        return np.array(self._xy)

    def iteration(self):
        self._xy.append(np.random.choice(self.f, p=self.p)(*self._xy[-1]))

    def generate(self, niterations):
        for n in range(int(niterations)):
            self.iteration()

    def plot(self, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots()
        ax.axis('off')
        ax.axis('equal')
        kw = dict(marker='.', ls='none', ms=.1, c='g')
        kw.update(kwargs)
        ax.plot(*fern.xy.T, **kw)
        return ax


if __name__ == '__main__':
    fern = BarnsleyFern()
    fern.generate(1e5)
    fern.plot()
    plt.show()
