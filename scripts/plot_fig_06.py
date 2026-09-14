import matplotlib.pyplot as mpl
from matplotlib.gridspec import GridSpec

from figure_tools.count_corr_data import load_cc_data
from figure_tools.definitions import (FIG_WIDTH_FULL,
                                      FONT_SIZE_LETTERS, LONGNAMES)
from figure_tools.plot_count_corr import plot_cc, plot_timecourse
from figure_tools import pvalue_log
from figure_tools.style import set_paper_style, save_figure


def main_with_timecourse(groups, cmp_pairs):

    fig = mpl.figure(figsize=(FIG_WIDTH_FULL, 3), dpi=250)

    LGAP = .08
    BOTTOM = .15
    TOP = .85
    RIGHT = .98
    WSPACE = .7
    HSPACE = .5

    stages = ('W', '3')

    grid = GridSpec(1, 4, left=LGAP, bottom=BOTTOM, right=RIGHT, top=TOP,
                    wspace=WSPACE, hspace=HSPACE,
                    width_ratios=[4, 2, 4, 4])

    fid_continuous = load_cc_data('wholetime_H')
    fid_ripples = load_cc_data('ripples')
    ax_continuous = fig.add_subplot(grid[2])
    ax_ripples = fig.add_subplot(grid[3])

    print('Plotting continuous count correlations')
    with pvalue_log.context(figure='fig_06', panel='b', region=LONGNAMES['H']):
        plot_cc(ax_continuous, fid_continuous, groups, cmp_pairs, stages, add_ripple_label=False)
    print('Plotting SWR count correlations')
    with pvalue_log.context(figure='fig_06', panel='c', region=LONGNAMES['HRipp']):
        plot_cc(ax_ripples, fid_ripples, groups, cmp_pairs, stages, add_ripple_label=True)

    ax_continuous.set_ylim((-.1, .2))
    ax_ripples.set_ylim((-.35, .7))

    plot_timecourse(fig, grid)

    _, tops, lefts, _ = grid.get_grid_positions(fig)

    left_shift = .07
    top_shift = .1

    letter_pos = {'A': lefts[0], 'B': lefts[2], 'C': lefts[3]}

    for letter in letter_pos:
        fig.text(letter_pos[letter] - left_shift, tops[0] + top_shift,
                 letter.lower(), weight='bold', size=FONT_SIZE_LETTERS)

    pvalue_log.write('fig_06')
    save_figure(fig, 'fig_06', dpi=250)


def main():
    groups = ['no_resp', 'inv']
    cmp_pairs = [('no_resp', 'inv')]

    # this is the main figure
    main_with_timecourse(groups, cmp_pairs)


if __name__ == '__main__':
    set_paper_style()
    main()
