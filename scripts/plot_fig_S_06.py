import matplotlib.pyplot as mpl
from matplotlib.gridspec import GridSpec

from figure_tools.definitions import (FIG_WIDTH_FULL,
                                      FONT_SIZE_REGIONS, LONGNAMES)
from figure_tools.plot_cohen import draw_stats
from figure_tools.population import load_population
from figure_tools import pvalue_log
from figure_tools.sleep_data import load_sleep_frates
from figure_tools.style import save_figure, set_paper_style, TYPE_COLORS, TYPE_NAMES


def main():

    df = load_sleep_frates()

    pop = load_population()

    df = df.merge(pop[['ident', 'is_selective', 'is_inv',
                       'is_no_resp', 'is_consistent', 'Simple_Region']], on='ident')

    reg_idxs = dict()
    regions = ('A', 'PHC', 'H')
    consider_idxs = ('inv', 'resp', 'no_resp')
    invariant_idxs = dict()
    for reg in regions:
        reg_idxs[reg] = df.Simple_Region == reg

    invariant_idxs['inv'] = df.is_inv & df.is_consistent
    invariant_idxs['resp'] = df.is_selective & df.is_consistent
    invariant_idxs['no_resp'] = df.is_no_resp

    fig = mpl.figure(figsize=(FIG_WIDTH_FULL, 7.5))
    grid = GridSpec(len(consider_idxs), 8, hspace=.5, wspace=.7, right=.95, left=.09,
            top=.88, bottom=.07, width_ratios=[1, 1, .00, 1, 1, .00, 1, 1])

    for ireg, reg in enumerate(regions):
        plot = fig.add_subplot(grid[0, (3*ireg):(3*ireg+2)])
        plot.text(.5, 1.4, LONGNAMES[reg], size=FONT_SIZE_REGIONS,
                weight='bold', ha='center', transform=plot.transAxes)
        plot.axis('off')

    param = {
        'label_long': False,
        'stats_compare_dist': -.13,
        'stage_angle': 20,
        'equal_shift': 0,
        'small_arrow_size': 7,
        'do_titles': False,
        'ypos_N': 1.09
    }
    param['perc_xlim'] = (-.3, 1.3)

    for i_idx, idxs in enumerate(consider_idxs):
        if i_idx == 0:
            param['do_heading'] = True
        else:
            param['do_heading'] = False
        if i_idx == 2:
            param['stats_do_xtext'] = True
        else:
            param['stats_do_xtext'] = False
        plots_dots = [fig.add_subplot(grid[i_idx, 3*ireg])
            for ireg in (0, 1, 2)]
        plots_perc = [fig.add_subplot(grid[i_idx, 3*ireg + 1])
            for ireg in (0, 1, 2)]
        param['invariant_name'] = idxs
        print(idxs, param)
        with pvalue_log.context(figure='fig_S_06'):
            draw_stats(plots_dots, plots_perc, df, reg_idxs, regions,
                    invariant_idxs[idxs], param)

        plots_dots[0].text(-.8, .5,
                TYPE_NAMES[idxs].replace(' neurons', '').capitalize(),
                transform=plots_dots[0].transAxes, rotation=90,
                ha='center', va='center', color=TYPE_COLORS[idxs],
                size=FONT_SIZE_REGIONS, weight='bold')

    pvalue_log.write('fig_S_06')
    save_figure(fig, 'fig_S_06', dpi=300)


if __name__ == '__main__':
    set_paper_style()
    main()
