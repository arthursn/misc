import random

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

__all__ = ["Mines"]


class _CoordsFormatter:
    """
    Formats coordinates in the interactive plot mode
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def __call__(self, x, y):
        string = ""
        try:
            i = int(round(y))
            j = int(round(x))
            if i >= 0 and i < self.height and j >= 0 and j < self.width:
                string = "    i = {}, j = {}".format(i, j)
        except Exception:
            pass
        return string


class Mines:
    """
    Minesweeper

    Parameters
    ----------
    width : int
        Width of minefield
    height : int
        Height of minefield
    n_mines : int
        Number of mines
    show : bool (optional)
        If True, displays game when initialized
    """

    # Colormap object used for showing wrong cells
    cmap_reds_alpha = LinearSegmentedColormap.from_list(
        name="Reds_alpha", colors=[[0, 0, 0, 0], [0.9, 0, 0, 1]]
    )

    # Figure dimensions (min width and height in inches and scale factor)
    figsize = {"minw": 4, "minh": 3, "scale": 0.7}

    # Color dictionary for coloring the revealed cells according with number
    # of mines in the neighboring cells
    color_dict = {
        1: [0, 0, 1],
        2: [0, 1, 0],
        3: [1, 0, 0],
        4: [0, 0, 0.5],
        5: [0.5, 0, 0],
        6: [0, 0, 0.66],
        7: [0, 0, 0.33],
        8: [0, 0, 0],
    }

    # Pre-defined levels (level: [width, height, mines])
    levels = {0: [8, 8, 10], 1: [16, 16, 40], 2: [30, 16, 99]}
    # Aliases for the levels
    level_aliases = {
        **dict.fromkeys(["beginner", "b", "0", 0], 0),
        **dict.fromkeys(["intermediate", "i", "1", 1], 1),
        **dict.fromkeys(["expert", "e", "2", 2], 2),
    }

    def __init__(self, width, height, n_mines, show=True):
        self.width = width
        self.height = height
        self.n = self.width * self.height
        self.n_mines = n_mines
        if self.n_mines >= self.n:
            raise Exception("n_mines must be < width*height")
        self.n_not_mines = self.n - self.n_mines

        self.ii, self.jj = np.mgrid[: self.height, : self.width]
        self.i, self.j = self.ii.ravel(), self.jj.ravel()

        self.mines = np.full(
            (self.height, self.width), False, dtype=bool
        )  # boolean, mine or not
        # number of mines in the neighboring cells
        self.mines_count = np.full((self.height, self.width), 0, dtype=int)
        self.flags = np.full((self.height, self.width), False, dtype=bool)  # mine flags
        self.revealed = np.full(
            (self.height, self.width), False, dtype=bool
        )  # revealed cells
        self.wrong = np.full(
            (self.height, self.width), False, dtype=bool
        )  # wrong guesses

        self.mines_pts = None  # once initialized, Lines2D object
        self.flags_pts = None  # Line2D objects
        self.mines_count_txt = np.full(
            (self.height, self.width), None, dtype=object
        )  # 2D array of Text objects
        self.revealed_img = None  # AxesImage object
        self.wrong_img = None  # AxesImage object
        self.title_txt = None  # Text object

        self.is_initialized = False  # if game is initialized
        self.is_game_over = False

        # Connection ids of mouse click and key press events
        self.cid_mouse = None
        self.cid_key = None

        self.fig, self.ax = plt.subplots(
            figsize=(
                max(self.width * self.figsize["scale"], self.figsize["minw"]),
                max(self.height * self.figsize["scale"], self.figsize["minh"]),
            )
        )
        self.fig.canvas.manager.set_window_title(
            "pymines {} × {} ({} mines)".format(self.width, self.height, self.n_mines)
        )

        self.draw_minefield()

        if show:
            plt.show()

    def refresh_canvas(self):
        """
        Updates minefield
        """
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def draw_minefield(self):
        """
        Draws initial empty minefield board
        """
        # Resets member variables to initial values
        self.is_initialized = False
        self.is_game_over = False
        self.mines[:, :] = False
        self.mines_count[:, :] = 0
        self.flags[:, :] = False
        self.revealed[:, :] = False

        # Clears plot, sets limits
        self.ax.clear()
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.ax.set_xlim(-0.6, self.width - 0.4)
        self.ax.set_ylim(-0.6, self.height - 0.4)

        # Draws grid lines
        for j in np.arange(-0.5, self.width):
            self.ax.plot([j, j], [-0.5, self.height - 0.5], lw=1, color="k")
        for i in np.arange(-0.5, self.height):
            self.ax.plot([-0.5, self.width - 0.5], [i, i], lw=1, color="k")

        # Connects mouse click and key press event handlers and coordinates formatter
        if self.cid_mouse is None:
            self.cid_mouse = self.fig.canvas.mpl_connect(
                "button_press_event", self.on_mouse_click
            )
            self.cid_key = self.fig.canvas.mpl_connect(
                "key_press_event", self.on_key_press
            )
            self.ax.format_coord = _CoordsFormatter(self.width, self.height)

        # Title text: number of flags/total mines
        self.title_txt = self.ax.set_title(
            "{}/{}".format(np.count_nonzero(self.flags), self.n_mines)
        )

        self.refresh_canvas()

    def initialize(self, i, j):
        """
        Initializes new game. This function is called after first click
        in order to prevent the first click being straight over a mine
        """
        population = set(range(self.n))
        population.remove(i * self.width + j)  # removes initial click
        idx = random.sample(list(population), self.n_mines)  # choose mines

        # Sets mines
        self.mines[self.i[idx], self.j[idx]] = True
        # Sets neighbor mines counter
        for i, j in zip(self.i, self.j):
            self.mines_count[i, j] = self.count_neighbor_mines(i, j)
        # Sets wrong guesses
        self.wrong = ~self.mines & self.flags

        # Initializes plot objects
        (self.flags_pts,) = self.ax.plot([], [], "k>", ms=8)
        self.revealed_img = self.ax.imshow(self.revealed, vmin=0, vmax=4, cmap="gray_r")
        self.wrong_img = self.ax.imshow(
            self.wrong, vmin=0, vmax=1, cmap=self.cmap_reds_alpha
        )

        # Initializes text objects of neighbor mines counter. They're
        # initially set as non visible. As the cells are revealed, their
        # status is changed to visible
        p_count = self.mines_count > 0
        for i, j, count in zip(
            self.ii[p_count], self.jj[p_count], self.mines_count[p_count]
        ):
            self.mines_count_txt[i, j] = self.ax.text(
                j,
                i,
                str(count),
                fontweight="bold",
                color=self.color_dict[count],
                ha="center",
                va="center",
                visible=False,
            )
        self.is_initialized = True

        self.refresh_canvas()

    def get_ij_neighbors(self, i, j):
        """
        Gets the i, j coordinates (i is row, y coordinate, j is column,
        x coordinate) of the neighboring cells
        """
        ii, jj = np.mgrid[i - 1 : i + 2, j - 1 : j + 2]
        ii, jj = ii.ravel(), jj.ravel()
        filtr = (ii >= 0) & (ii < self.height) & (jj >= 0) & (jj < self.width)
        ij_neighbors = set(zip(ii[filtr], jj[filtr]))
        ij_neighbors.remove((i, j))
        return ij_neighbors

    def count_neighbor_mines(self, i, j):
        """
        Counts the number of mines in the neighboring cells
        """
        n_neighbor_mines = -1
        if not self.mines[i, j]:
            n_neighbor_mines = np.count_nonzero(
                self.mines[
                    (i - 1 if i > 0 else 0) : i + 2, (j - 1 if j > 0 else 0) : j + 2
                ]
            )
        return n_neighbor_mines

    def count_neighbor_flags(self, i, j):
        """
        Counts the number of flags in the neighboring cells
        """
        return np.count_nonzero(
            self.flags[(i - 1 if i > 0 else 0) : i + 2, (j - 1 if j > 0 else 0) : j + 2]
        )

    def update_revealed(self, i, j):
        """
        Updates revealed cells by checking i, j cell and, recursevely,
        the contiguous cells without mines
        """
        if not self.revealed[i, j]:
            # If not revealed cell
            if self.mines_count[i, j] < 0:
                # If wrong guess, games is over
                self.wrong = ~self.mines & self.flags
                self.wrong[i, j] = True
                self.game_over()
            else:
                # If guess is correct
                self.revealed[i, j] = True
                if self.mines_count[i, j] == 0:
                    # Recursively looks for contiguous cells without mines
                    for _i, _j in self.get_ij_neighbors(i, j):
                        if self.mines_count[_i, _j] >= 0 and not self.revealed[_i, _j]:
                            self.flags[_i, _j] = False
                            self.update_revealed(_i, _j)
                elif self.mines_count[i, j] > 0:
                    # The line below only makes sense when it's in the middle of the
                    # recursion. For instance, a cell is flagged, but it is part of a
                    # big blob that's going to be revealed. The game doesn't punish
                    # the player in this scenario. This behavior has been copied
                    # from gnome-mines
                    self.flags[i, j] = False
                    # Reveals mine count
                    self.mines_count_txt[i, j].set_visible(True)
        elif self.mines_count[i, j] == self.count_neighbor_flags(i, j):
            # If cell that's already revealed is clicked and the number of
            # neighboring flags is the same as the number of neighboring
            # mines, then the hidden neighbor cells are recursevely
            # revealed. Evidently, if any flag guess is wrong, the game is
            # over.
            for _i, _j in self.get_ij_neighbors(i, j):
                if not self.flags[_i, _j] and not self.revealed[_i, _j]:
                    self.update_revealed(_i, _j)

    def reveal(self, i, j):
        """
        Reveals clicked cell and contiguous cells without mines
        """
        if not self.is_game_over:
            if not self.flags[i, j]:
                # Game is initialized after first click in order to prevent
                # the first click being straight over a mine
                if not self.is_initialized:
                    self.initialize(i, j)

                self.update_revealed(i, j)
                self.revealed_img.set_data(self.revealed)
                self.flags_pts.set_data(*np.where(self.flags)[::-1])
                self.refresh_canvas()

            if np.count_nonzero(self.revealed) == self.n_not_mines:
                self.game_over(True)

    def flag(self, i, j):
        """
        Flags i, j cell
        """
        # Does not allow starting a game with a flag
        if not self.is_game_over and self.is_initialized:
            if not self.revealed[i, j]:
                self.flags[i, j] = not self.flags[i, j]
                self.flags_pts.set_data(*np.where(self.flags)[::-1])
                self.title_txt.set_text(
                    "{}/{}".format(np.count_nonzero(self.flags), self.n_mines)
                )
                self.refresh_canvas()

    def game_over(self, win=False):
        """
        Callback when game is over
        """
        self.is_game_over = True

        if win:
            self.flags_pts.set_data(
                *np.where(self.mines)[::-1]
            )  # shows mines marked with flags
            self.title_txt.set_text("You win! Press F2 to start a new game")
        else:
            self.wrong_img.set_data(self.wrong)  # wrong guesses
            self.mines_pts = self.ax.plot(
                self.jj[self.mines & ~self.flags],
                self.ii[self.mines & ~self.flags],
                "kX",
                ms=10,
            )  # shows mines
            self.title_txt.set_text("You lose! Press F2 to start a new game")

        self.refresh_canvas()

    def on_mouse_click(self, event):
        """
        Callback when mouse is clicked
        """
        if not self.is_game_over:
            try:
                # i, j coordinates of the click event
                i = int(round(event.ydata))
                j = int(round(event.xdata))

                # Left button
                if event.button == 1 or event.button == 2:
                    self.reveal(i, j)

                # Right button
                elif event.button == 3:
                    self.flag(i, j)

            except (TypeError, IndexError):
                pass

    def on_key_press(self, event):
        """
        Callback when key is pressed
        """
        # F2 for starting new game
        if event.key == "f2":
            self.draw_minefield()

    @staticmethod
    def new_game(*args, level="beginner", show=True):
        """
        Static method for initializing the game with custom settings or in pre-defined levels
        (beginner, intermediate, expert)
        """
        if len(args) == 3:
            minefield = args
        else:
            minefield = Mines.levels[Mines.level_aliases[level]]
        return Mines(*minefield, show)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        metavar="level (b, i, e)",
        default="beginner",
        help="level, i.e., "
        "beginner (8 x 8, 10 mines), intermediate (16 x 16, 40 mines), expert (30 "
        "x 16, 99 mines)",
    )
    parser.add_argument(
        "-c",
        metavar=("width", "height", "mines"),
        default=[],
        type=int,
        nargs=3,
        help="custom game, provided width, height, and number of mines",
    )
    args = parser.parse_args()

    game = Mines.new_game(*args.c, level=args.l)
