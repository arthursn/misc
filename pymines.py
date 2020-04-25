#!/usr/bin/env python3

import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


class Mines:
    """
    Minesweeper

    Parameters
    ----------
    width : int
        Width of minefield
    height : int
        Height of minefield
    N_mines: int
        Number of mines
    """
    __color_array = np.array([[0, 0, 0, 0], [.9, 0, 0, 1]])
    # Colormap object used for showing wrong cells
    cmap_reds_alpha = LinearSegmentedColormap.from_list(name='Reds_alpha', colors=__color_array)

    figsize = dict(minw=4, minh=3, scale=.7)

    # Color dictionary for coloring the revealed cells according with number
    # of mines in the neighboring cells
    color_dict = {1: [0, 0, 1], 2: [0, 1, 0], 3: [1, 0, 0], 4: [0, 0, .5],
                  5: [.5, 0, 0], 6: [0, 0, .66], 7: [0, 0, .33], 8: [0, 0, 0]}

    # Pre-defined levels
    levels = {**dict.fromkeys(['beginner', 'b', '0'], [8, 8, 10]),
              **dict.fromkeys(['intermediate', 'i', '1'], [16, 16, 40]),
              **dict.fromkeys(['expert', 'e', '2'], [30, 16, 99])}

    def __init__(self, width, height, N_mines):
        self.width = width
        self.height = height
        self.N = self.width*self.height
        self.N_mines = N_mines
        if self.N_mines >= self.N:
            raise Exception('N_mines must be < width*height')
        self.N_not_mines = self.N - self.N_mines

        self.ii, self.jj = np.mgrid[:self.height, :self.width]
        self.i, self.j = self.ii.ravel(), self.jj.ravel()

        self.mines = np.full((self.height, self.width), False, dtype=bool)  # boolean, mine or not
        self.mines_count = np.full((self.height, self.width), 0, dtype=int)  # number of mines in the neighboring cells
        self.flags = np.full((self.height, self.width), False, dtype=bool)  # mine flags
        self.revealed = np.full((self.height, self.width), False, dtype=bool)  # revealed cells
        self.wrong = np.full((self.height, self.width), False, dtype=bool)  # wrong guesses

        self.mines_pts = None  # once initialized, Lines2D object
        self.flags_pts = None  # Line2D objects
        self.mines_count_txt = np.full((self.height, self.width), None, dtype=object)  # 2D array of Text objects
        self.revealed_img = None  # AxesImage object
        self.wrong_img = None  # AxesImage object
        self.title_txt = None  # Text object

        self.is_initialized = False  # if game is initialized
        self.is_game_over = False

        # Connection ids of mouse click and key press events
        self.cid_mouse = None
        self.cid_key = None

        self.fig, self.ax = plt.subplots(figsize=(max(self.width*self.figsize['scale'], self.figsize['minw']),
                                                  max(self.height*self.figsize['scale'], self.figsize['minh'])))
        self.fig.canvas.set_window_title(u'pymines {} × {} ({} mines)'.format(self.width, self.height, self.N_mines))

        self.draw_minefield()

        plt.show()

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

        # Clears plot window, sets limits
        self.ax.clear()
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_xlim(-.6, self.width - .4)
        self.ax.set_ylim(-.6, self.height - .4)

        # Draw grid lines
        for j in np.arange(-.5, self.width):
            self.ax.plot([j, j], [-.5, self.height-.5], lw=.5, color='k')
        for i in np.arange(-.5, self.height):
            self.ax.plot([-.5, self.width-.5], [i, i], lw=.5, color='k')

        # Connects mouse click and key press event handlers
        if self.cid_mouse is None:
            self.cid_mouse = self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_click)
            self.cid_key = self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

        # Title text is number of flags/total mines
        self.title_txt = self.ax.set_title('{}/{}'.format(np.count_nonzero(self.flags), self.N_mines))

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def initialize(self, i, j):
        """
        Initializes new game. This function is called after first click
        in order to prevent the first click being straight over a mine
        """
        population = set(range(self.N))
        population.remove(i*self.width + j)  # removes initial click
        idx = random.sample(population, self.N_mines)  # choose mines

        # Set mines
        self.mines[self.i[idx], self.j[idx]] = True
        # Set neighbor mines counter
        for idx in range(self.N):
            i, j = self.i[idx], self.j[idx]
            self.mines_count[i, j] = self.count_neighbor_mines(i, j)
        self.wrong = ~self.mines & self.flags

        # Initializes plot objects
        self.flags_pts, = self.ax.plot([], [], 'k>', ms=8)
        self.revealed_img = self.ax.imshow(self.revealed, vmin=0, vmax=4, cmap='gray_r')
        self.wrong_img = self.ax.imshow(self.wrong, vmin=0, vmax=1, cmap=self.cmap_reds_alpha)

        # Initializes text objects of neighbor mines counter. They're initially
        # set as non visible
        p_count = self.mines_count > 0
        for i, j, count in zip(self.ii[p_count], self.jj[p_count], self.mines_count[p_count]):
            self.mines_count_txt[i, j] = self.ax.text(j, i, str(count), fontweight='bold',
                                                      color=self.color_dict[count], ha='center', va='center',
                                                      visible=False)
        self.is_initialized = True

    def get_ij_neighbors(self, i, j):
        """
        Gets i, j coordinates (i is row, y coordinate, j is column, x 
        coordinate) of 
        """
        ii, jj = np.mgrid[i-1:i+2, j-1:j+2]
        ii, jj = ii.ravel(), jj.ravel()
        filtr = (ii >= 0) & (ii < self.height) & (jj >= 0) & (jj < self.width)
        ij_neighbors = set(zip(ii[filtr], jj[filtr]))
        ij_neighbors.remove((i, j))
        return ij_neighbors

    def count_neighbor_mines(self, i, j):
        """
        Counts number of mines in the neighboring cells
        """
        n_neighbor_mines = -1
        if not self.mines[i, j]:
            n_neighbor_mines = np.count_nonzero(self.mines[(i-1 if i > 0 else 0):i+2, (j-1 if j > 0 else 0):j+2])
        return n_neighbor_mines

    def count_neighbor_flags(self, i, j):
        """
        Counts the number of flags in the neighboring cells
        """
        return np.count_nonzero(self.flags[(i-1 if i > 0 else 0):i+2, (j-1 if j > 0 else 0):j+2])

    def game_over(self, win=False):
        """
        Callback when game is over
        """
        self.is_game_over = True
        if win:
            self.flags_pts.set_data(*np.where(self.mines)[::-1])  # shows mines marked with flags
            self.title_txt.set_text('You win! Press F2 to start a new game')
        else:
            self.wrong_img.set_data(self.wrong)  # wrong guesses
            self.mines_pts = self.ax.plot(self.jj[self.mines & ~self.flags],
                                          self.ii[self.mines & ~self.flags],
                                          'kX', ms=8)  # shows mines
            self.title_txt.set_text('You lose! Press F2 to start a new game')

    def reveal(self, i, j):
        """
        Reveals clicked cell and contiguous cells without mines
        """
        if not self.revealed[i, j]:
            # If not revealed cell
            if self.mines_count[i, j] < 0:
                # If wrong guess, games is over
                self.wrong = ~self.mines & self.flags
                self.wrong[i, j] = True
                self.game_over()
            else:
                # If correct guess
                self.revealed[i, j] = True
                if self.mines_count[i, j] == 0:
                    # Recursively looks for contiguous cells without mines
                    for _i, _j in self.get_ij_neighbors(i, j):
                        if self.mines_count[_i, _j] >= 0 and not self.revealed[_i, _j]:
                            self.flags[_i, _j] = False
                            self.reveal(_i, _j)
                elif self.mines_count[i, j] > 0:
                    self.flags[i, j] = False
                    self.mines_count_txt[i, j].set_visible(True)
        elif self.mines_count[i, j] == self.count_neighbor_flags(i, j):
            # If revealed cell is clicked, if number neighboring flags is the
            # same as the number of neighboring mines, then reveals concealed
            # neighbor cells
            for _i, _j in self.get_ij_neighbors(i, j):
                if not self.flags[_i, _j] and not self.revealed[_i, _j]:
                    self.reveal(_i, _j)

    def on_mouse_click(self, event):
        """
        Callback when mouse is clicked
        """
        try:
            # i, j coordinates of the click event
            i = np.round(event.ydata).astype(int)
            j = np.round(event.xdata).astype(int)

            # Games is initialized after first click in order to prevent
            # the first click being straight over a mine
            if not self.is_initialized:
                self.initialize(i, j)

            if not self.is_game_over:
                # Left button
                if event.button == 1 or event.button == 2:
                    if not self.flags[i, j]:
                        self.reveal(i, j)
                        self.revealed_img.set_data(self.revealed)
                        self.flags_pts.set_data(*np.where(self.flags)[::-1])
                # Right button
                elif event.button == 3:
                    if not self.revealed[i, j]:
                        self.flags[i, j] = not self.flags[i, j]
                        self.flags_pts.set_data(*np.where(self.flags)[::-1])
                        self.title_txt.set_text('{}/{}'.format(np.count_nonzero(self.flags), self.N_mines))

                if np.count_nonzero(self.revealed) == self.N_not_mines:
                    self.game_over(True)

                # Updates minefield
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
        except (TypeError, IndexError):
            pass

    def on_key_press(self, event):
        """
        Callback when key is pressed
        """
        # F2 for reseting the game
        if event.key == 'f2':
            self.draw_minefield()

    @staticmethod
    def new_game(level='beginner'):
        """
        Static method for initializing the game in pre-defined levels
        (beginner, intermediate, expert)
        """
        return Mines(*Mines.levels[level])


if __name__ == '__main__':
    import sys

    if len(sys.argv) == 2:
        game = Mines.new_game(sys.argv[1])
    elif len(sys.argv) == 4:
        game = Mines(*map(int, sys.argv[1:]))
    else:
        if len(sys.argv) > 1:
            print('Invalid arguments. Starting game in the beginner level.')
        game = Mines.new_game()
