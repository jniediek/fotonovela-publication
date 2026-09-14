import numpy as np
import matplotlib.pyplot as mpl
from matplotlib.gridspec import GridSpec

from figure_tools.definitions import (FIG_WIDTH_FULL, FOLDER_STIM_PICTURES,
                                      MATERIALS_DIR)

from figure_tools.style import save_figure, set_paper_style


def plot_one_item(plot, img_fname, title, text):
    img = mpl.imread(img_fname)
    plot.imshow(np.zeros(shape=(1, 1, 3), dtype=np.uint8),
            aspect='auto', extent=(0, 200, 0, 200))
    plot.imshow(img, aspect='auto', extent=(60, 100, 33, 73))
    plot.set_xlim((0, 160))
    plot.set_ylim((0, 90))
    plot.axis('off')
    plot.text(80, 85, title,
            ha='center', va='top', color='w',
            size=8, weight='bold')
    text = text.replace('\\n', '\n').replace('\n\n', '\n')
    plot.text(80, 30, text,
            ha='center', va='top', color='w',
            size=6.3)


def plot_story():

    pat, ses = 717, 2
    infix = '{:03d}fn{}'.format(pat, ses)

    story_file_name = MATERIALS_DIR / (infix + '_translated.txt')

    with open(story_file_name, 'r') as fid:
        story = fid.readlines()

    story = [line.strip() for line in story]
    grid = GridSpec(5, 2, hspace=.1, wspace=.4,
            left=.12, right=.9, top=.99, bottom=.01)

    fig = mpl.figure(figsize=(FIG_WIDTH_FULL, 6.6), facecolor='lightgrey')

    i = 0

    while len(story):
        plot = fig.add_subplot(grid[i % 5, i//5])
        plot.text(-.05, .99, '{}.'.format(i + 1), ha='right', va='top',
                transform=plot.transAxes, size=10, weight='bold')
        plot_one_item(plot,
            FOLDER_STIM_PICTURES / story[0],
            story[1], story[2])
        story = story[4:]

        i = i + 1
    save_figure(fig, 'fig_S_01')


if __name__ == '__main__':
    set_paper_style()
    plot_story()
