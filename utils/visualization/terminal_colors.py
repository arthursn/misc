import sys
import numpy as np
import matplotlib.pyplot as plt


def get_color_code(r, g, b):
    """
    Converts rgb (0 - 1 values) to terminal colorcode
    """
    return 16 + int(round(5 * r) * 36 + round(5 * g) * 6 + round(5 * b))


if __name__ == '__main__':
    for cmap_id in plt.colormaps():
        cmap = plt.get_cmap(cmap_id)
        sys.stdout.write('{:19s}'.format(cmap_id))
        for x in np.linspace(0, 1, 100):
            r, g, b, _ = cmap(x)
            sys.stdout.write(u'\u001b[48;5;{}m '.format(get_color_code(r, g, b)))
        sys.stdout.write(u'\u001b[0m\n')
