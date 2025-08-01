import argparse
import subprocess
from pathlib import Path

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
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
            raise Exception("Shapes do not match")

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
        slice_i = slice(max(i - 1, 0), i + 2, 1)
        slice_j = slice(max(j - 1, 0), j + 2, 1)
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

    def animate(
        self,
        save=None,
        cycle=False,
        nframes=None,
        freezeframes=0,
        interval=80,
        dpi=90,
        color_dead="white",
        color_alive="black",
    ):
        """
        Animate Game of Life

        Parameters
        ----------
        save: str (optional)
            If None is provided, the animation is not saved. If a string is
            provided, interprets it as the filename to be saved
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
        color_dead: list or str (optional)
            Color of the dead cells as RGB colors (values from 0 to 1), color
            name, or hex code
            Default: white
        color_alive: list or str (optional)
            Color of the alive cells as RGB colors (values from 0 to 1), color
            name, or hex code
            Default: black
        """
        figsize = np.array(self.cells.shape[::-1])
        figsize = figsize * 10 / figsize.max()

        fig, ax = plt.subplots(figsize=figsize)
        ax.axis("off")

        color_dead = colors.to_rgb(color_dead)
        color_alive = colors.to_rgb(color_alive)

        def colorize_cells(cells):
            color_data = np.ones((*cells.shape, 3))
            color_data[~self.cells] *= np.array(color_dead)
            color_data[self.cells] *= np.array(color_alive)
            return (color_data * 255).astype(np.uint8)

        img = ax.imshow(colorize_cells(self.cells))
        cells_init = self.cells.copy()

        def func(*args):
            if args[0] <= freezeframes:
                if args[0] == 0:
                    self.cells = cells_init
            else:
                self.step()
            img.set_data(colorize_cells(self.cells))
            return (img,)

        kwargs = dict(fig=fig, func=func, blit=True, interval=interval)
        if nframes is not None:
            kwargs["frames"] = range(nframes)

        ani = animation.FuncAnimation(**kwargs)

        fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)

        if save is not None:
            fout = save

            savefig_kwargs = dict(pad_inches=0)
            if cycle:
                fout_tmp = Path(".gol_tmp.gif")
                ani.save(
                    fout_tmp,
                    writer="imagemagick",
                    dpi=dpi,
                    savefig_kwargs=savefig_kwargs,
                )
                subprocess.call(
                    f"convert {fout_tmp} -coalesce -duplicate 1,-2-1 {fout}", shell=True
                )
                fout_tmp.unlink()
            else:
                ani.save(
                    fout, writer="imagemagick", dpi=dpi, savefig_kwargs=savefig_kwargs
                )

        return ani


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "fname",
        metavar="fig1.[jpg,png,...], fig1.[jpg,png,...], ...",
        nargs="*",
        help="input images used as initial state to game of life",
    )
    parser.add_argument(
        "-s",
        "--save",
        metavar="game_of_life.gif",
        nargs="?",
        const="?",
        help="save as gif. If no argument is provided, saves using [fname] as a base file name",
    )
    parser.add_argument(
        "-c",
        "--cycle",
        action="store_true",
        help="patrol-cycle (forwards and backwards) animation",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="if true, does not show animation as matplotlib interactive window",
    )
    parser.add_argument(
        "-n",
        "--nframes",
        type=int,
        help="number of frames",
    )
    parser.add_argument(
        "-f",
        "--freezeframes",
        type=int,
        default=0,
        help="number of frozen frames at the beginning of the animation",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=80,
        help="interval (in milliseconds) between frames",
    )
    parser.add_argument(
        "-d",
        "--dpi",
        type=float,
        default=90,
        help="output gif resolution in pixels per inch",
    )
    parser.add_argument(
        "-cd",
        "--color_dead",
        default="white",
        help="color of the dead cells as hex code or color name",
    )
    parser.add_argument(
        "-ca",
        "--color_alive",
        default="black",
        help="color of the alive cells as hex code or color name",
    )
    args = parser.parse_args()

    if len(args.fname) == 0:
        gol = GameOfLife(14, 38)

        cells_init = gol.cells_template()
        cells_init[5 : 5 + 2, 1 : 1 + 2] = True
        cells_init[5 : 5 + 3, 11 : 11 + 1] = True
        cells_init[4 : 4 + 1, 12 : 12 + 1] = True
        cells_init[8 : 8 + 1, 12 : 12 + 1] = True
        cells_init[3 : 3 + 1, 13 : 13 + 2] = True
        cells_init[9 : 9 + 1, 13 : 13 + 2] = True
        cells_init[6 : 6 + 1, 15 : 15 + 1] = True
        cells_init[4 : 4 + 1, 16 : 16 + 1] = True
        cells_init[8 : 8 + 1, 16 : 16 + 1] = True
        cells_init[5 : 5 + 3, 17 : 17 + 1] = True
        cells_init[6 : 6 + 1, 18 : 18 + 1] = True
        cells_init[3 : 3 + 3, 21 : 21 + 2] = True
        cells_init[2 : 2 + 1, 23 : 23 + 1] = True
        cells_init[6 : 6 + 1, 23 : 23 + 1] = True
        cells_init[1 : 1 + 2, 25 : 25 + 1] = True
        cells_init[6 : 6 + 2, 25 : 25 + 1] = True
        cells_init[3 : 3 + 2, 35 : 35 + 2] = True
        gol.initialize_cells(cells_init)

        save = "glider.gif" if args.save == "?" else args.save
        ani = gol.animate(
            save,
            args.cycle,
            args.nframes,
            args.freezeframes,
            args.interval,
            args.dpi,
        )

        if args.quiet:
            plt.show()

    for fname in args.fname:
        save = Path(fname).with_suffix(".gif") if args.save == "?" else args.save
        gol = GameOfLife.from_image(fname)
        ani = gol.animate(
            save,
            args.cycle,
            args.nframes,
            args.freezeframes,
            args.interval,
            args.dpi,
            args.color_dead,
            args.color_alive,
        )

    if not args.quiet:
        plt.show()
