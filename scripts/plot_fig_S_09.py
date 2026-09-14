import matplotlib.pyplot as mpl
from matplotlib.gridspec import GridSpec

from figure_tools.count_corr_data import load_cc_data
from figure_tools.definitions import (FIG_WIDTH_FULL,
                                      FONT_SIZE_LETTERS, FONT_SIZE_REGIONS,
                                      LONGNAMES)
from figure_tools.plot_count_corr import plot_cc
from figure_tools import pvalue_log
from figure_tools.style import save_figure, set_paper_style, TYPE_COLORS, TYPE_LETTERS, TYPE_NAMES


def main_without_timecourse(groups, cmp_pairs):

    fig = mpl.figure(figsize=(FIG_WIDTH_FULL, 7), dpi=150, constrained_layout=True)

    options = {'rsc_label_xpos': -.15}
    LGAP = .08
    BOTTOM = .15
    TOP = .9
    RIGHT = .98
    WSPACE = .4
    HSPACE = .65

    stages = ('W', '3')

    grid = GridSpec(2, 2, left=LGAP, bottom=BOTTOM, right=RIGHT, top=TOP,
                    wspace=WSPACE, hspace=HSPACE)

    # have to turn this into loading for all regions
    cont_data = dict()
    axes = dict()
    continuous_regions = ('A', 'PHC', 'H')

    for ireg, reg in enumerate(continuous_regions):
        cont_data[reg] = load_cc_data(f'wholetime_{reg}')
        axes[reg] = fig.add_subplot(grid[ireg])

        axes[reg].text(.5, 1.2, LONGNAMES[reg], weight='bold',
            size=FONT_SIZE_REGIONS, va='bottom', ha='center',
            transform=axes[reg].transAxes)


        # axes[reg].set_title(LONGNAMES[reg])
        axes[reg].set_ylim((-0.1, .4))
        print(reg)
        with pvalue_log.context(figure='fig_S_09', panel='abc'[ireg],
                                region=LONGNAMES[reg]):
            plot_cc(axes[reg], cont_data[reg], groups, cmp_pairs, stages,
                     add_ripple_label=False, options=options)
        print('\n\n')

    fid_ripples = load_cc_data('ripples')
    ax_ripples = fig.add_subplot(grid[3])
    # ax_ripples.set_title('Hipp. ripples')
    ax_ripples.text(.5, 1.2, 'Hipp. ripples', weight='bold',
            size=FONT_SIZE_REGIONS, va='bottom', ha='center',
            transform=ax_ripples.transAxes)


    ax_ripples.set_ylim((-0.35, 0.6))

    print('Hipp. ripples')
    with pvalue_log.context(figure='fig_S_09', panel='d',
                            region=LONGNAMES['HRipp']):
        plot_cc(ax_ripples, fid_ripples, groups, cmp_pairs, stages,
                add_ripple_label=True, options=options)
    print('\n\n')

    _, tops, lefts, _ = grid.get_grid_positions(fig)

    left_shift = .07
    top_shift = .08

    letters_x = {'A': lefts[0], 'B': lefts[1], 'C': lefts[0], 'D': lefts[1]}
    letters_y = {'A': tops[0], 'B': tops[0], 'C': tops[1], 'D': tops[1]}

    for letter in 'ABCD':
        fig.text(letters_x[letter] - left_shift, letters_y[letter] + top_shift,
                 letter.lower(), weight='bold', size=FONT_SIZE_LETTERS)

    legend_plot = ax_ripples

    # legend_plot.axis('off')
    for cl in groups:
        label = f'{TYPE_LETTERS[cl]}, {TYPE_NAMES[cl].capitalize()}'
        legend_plot.plot([-10, -10], [-9, -9], color=TYPE_COLORS[cl],
                label=label)

        lgd = legend_plot.legend(loc='lower left',
                bbox_to_anchor=(.3, -.55))

        texts = lgd.get_texts()
        for text, cl in zip(texts, groups):
            text.set_color(TYPE_COLORS[cl])

    pvalue_log.write('fig_S_09')
    save_figure(fig, 'fig_S_09', dpi=250)


def main():
    # this is the supp. figure
    groups = ['no_resp', 'resp', 'inv']
    cmp_pairs = (('no_resp', 'resp'), ('no_resp', 'inv'))
    main_without_timecourse(groups, cmp_pairs)


if __name__ == '__main__':
    set_paper_style()
    main()
