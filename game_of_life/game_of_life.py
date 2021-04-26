import argparse
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pathlib import Path
from PIL import Image, ImageOps


class GameOfLife(object):
    def __init__(self, nrows, ncols):
        """
        Initialize empty Game of Life with a nrows by ncols grid.

        Parameters
        ----------
        nrows: int
            Number of rows.
        ncols: int
            Number of columns.
        """
        self.nrows = nrows
        self.ncols = ncols

        self.cells_init = self.cells_template()
        self.cells = self.cells_template()

    def cells_template(self):
        """
        Initialize empty cells template.

        Returns
        -------
        cells: numpy.ndarray shape(nrows, ncols)
            Empty cells template.
        """
        return np.full([self.nrows, self.ncols], False, dtype=bool)

    def initialize_cells(self, cells_init):
        """
        Initialize cells from initial configuration.

        Parameters
        ----------
        cells_init: numpy.ndarray shape(nrows, ncols)
            Initial cells configuration.
        """
        if self.cells.shape == cells_init.shape:
            self.cells_init = cells_init.copy()
            self.cells = cells_init.copy()
        else:
            raise Exception('Shapes do not match')

    def count_alive_neighbours(self, i, j):
        """
        Count number of alive cells in the neighbourhood.

        Parameters
        ----------
        i, j: int, int
            i, j (row, column) coordinates of cell.

        Returns
        -------
        n: int
            Number of alive neighbouring cells.
        """
        slice_i = slice(max(i-1, 0), i+2, 1)
        slice_j = slice(max(j-1, 0), j+2, 1)
        return np.count_nonzero(self.cells[slice_i, slice_j]) - int(self.cells[i, j])

    def step(self):
        """
        Compute cellular automaton step.
        """
        cells_ = self.cells.copy()

        for i in range(self.nrows):
            for j in range(self.ncols):
                nalive = self.count_alive_neighbours(i, j)
                # self.neighbours[i, j] = nalive

                if self.cells[i, j]:
                    # Any live cell with fewer than two live neighbours dies, as if by
                    # underpopulation. Any live cell with more than three live neighbours
                    # dies, as if by overpopulation. Any live cell with two or three live
                    # neighbours lives on to the next generation.
                    if nalive < 2 or nalive > 3:
                        cells_[i, j] = False
                else:
                    # Any dead cell with exactly three live neighbours becomes a live cell,
                    # as if by reproduction.
                    if nalive == 3:
                        cells_[i, j] = True

        self.cells = cells_

    @staticmethod
    def from_image(fname, threshold=128):
        """
        Static method. Initialize game of live from image.

        Parameters
        ----------
        fname: str
            Image file name
        threshold: int (optional)
            Threshold value for converting from grayscale to black and white
            White pixels are considered to be alive cells, while black pixels
            are dead cells.
            Default: 128

        Returns
        -------
        gol: GameOfLife
            Instance of GameOfLife
        """
        img = Image.open(fname)
        img = ImageOps.grayscale(img)
        arr = np.array(img)
        cells_init = np.full(arr.shape, False)
        cells_init[arr < threshold] = True

        gol = GameOfLife(*cells_init.shape)
        gol.initialize_cells(cells_init)

        return gol

    def animate(self, basefname=None, cycle=False, nframes=None, freezeframes=0, interval=80):
        """
        Animate Game of Life

        Parameters
        ----------
        basefname: str (optional)
            Base filename of file to be saved as gif. If None is provided,
            then the animation is not saved.
            Default: None
        cycle: bool (optional)
            If True, animates as patrol-cycle (forwards, then backwards).
            Only works if basefname is not None, i.e., if animation if saved
            as gif
            Default: False
        nframes: int (optional)
            Number of frames in animation. If None is provided, the animation
            continues until is interrupted, if animation is not saved,
            otherwise, number of frames is 100.
            Default: None
        freezeframes: int (optional)
            Number of frozen frames at beginning of animation.
            Default: 0
        interval: float (optional)
            Interval (in milliseconds) between frames.
            Default: 80
        """
        figsize = np.array(self.cells.shape[::-1])
        figsize = figsize * 10 / figsize.max()

        fig, ax = plt.subplots(figsize=figsize)
        ax.axis('off')

        img = ax.imshow(self.cells, cmap='gray_r', interpolation='nearest')
        cells_init = self.cells.copy()

        def func(*args):
            if args[0] <= freezeframes:
                if args[0] == 0:
                    self.cells = cells_init
            else:
                self.step()
            img.set_data(self.cells)
            return img,

        kwargs = dict(fig=fig,
                      func=func,
                      blit=True,
                      interval=interval)
        if nframes is not None:
            kwargs['frames'] = range(nframes)

        ani = animation.FuncAnimation(**kwargs)

        fig.tight_layout()

        if basefname is not None:
            fout = Path(basefname).with_suffix('.gif')

            savefig_kwargs = dict(pad_inches=0)
            if cycle:
                fout_tmp = Path('gol_tmp.gif')
                ani.save(fout_tmp, writer='imagemagick', savefig_kwargs=savefig_kwargs)
                subprocess.call(f'convert {fout_tmp} -coalesce -duplicate 1,-2-1 {fout}',
                                shell=True)
                fout_tmp.unlink()
            else:
                ani.save(fout, writer='imagemagick', savefig_kwargs=savefig_kwargs)

        return ani


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('fname', nargs='*', help='input images used as initial state to game of '
                        'life')
    parser.add_argument('-s', '--save', action='store_true', help='save as gif')
    parser.add_argument('-c', '--cycle', action='store_true', help='patrol-cycle (forwards and '
                        'backwards) animation')
    parser.add_argument('-n', '--nframes', type=int, help='number of frames')
    parser.add_argument('-f', '--freezeframes', type=int, default=0, help='number of frozen '
                        'frames at the beginning of the animation')
    parser.add_argument('-i', '--interval', type=float, default=80, help='interval (in '
                        'milliseconds) between frames')
    args = parser.parse_args()

    if len(args.fname) == 0:
        gol = GameOfLife(14, 38)

        cells_init = gol.cells_template()
        cells_init[5:5+2, 1:1+2] = True
        cells_init[5:5+3, 11:11+1] = True
        cells_init[4:4+1, 12:12+1] = True
        cells_init[8:8+1, 12:12+1] = True
        cells_init[3:3+1, 13:13+2] = True
        cells_init[9:9+1, 13:13+2] = True
        cells_init[6:6+1, 15:15+1] = True
        cells_init[4:4+1, 16:16+1] = True
        cells_init[8:8+1, 16:16+1] = True
        cells_init[5:5+3, 17:17+1] = True
        cells_init[6:6+1, 18:18+1] = True
        cells_init[3:3+3, 21:21+2] = True
        cells_init[2:2+1, 23:23+1] = True
        cells_init[6:6+1, 23:23+1] = True
        cells_init[1:1+2, 25:25+1] = True
        cells_init[6:6+2, 25:25+1] = True
        cells_init[3:3+2, 35:35+2] = True
        gol.initialize_cells(cells_init)

        ani = gol.animate('glider' if args.save else None, args.cycle,
                          args.nframes, args.freezeframes, args.interval)
    else:
        for fname in args.fname:
            gol = GameOfLife.from_image(fname)
            ani = gol.animate(fname if args.save else None, args.cycle,
                              args.nframes, args.freezeframes, args.interval)
    plt.show()
