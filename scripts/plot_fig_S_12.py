import numpy as np
import scipy.stats
import matplotlib.pyplot as mpl
from matplotlib.gridspec import GridSpec

from figure_tools.ccg_data import read_csvs
from figure_tools.definitions import (FIG_WIDTH_FULL,
                                      FONT_SIZE_REGIONS, LONGNAMES)
from figure_tools.plot_ccg import prepare_plot
from figure_tools.plot_stats import pstars
from figure_tools import pvalue_log
from figure_tools.style import (LW_LINE, save_figure, set_paper_style, STAGE_COLORS,
                                STAGE_LONGNAMES)

LEFT = .08
RIGHT = .98
ttop = .88
tbot = .18
WSPACE = .5
HSPACE = .7
spacing = (ttop - tbot)/3

pos_dict_A = {'left': LEFT, 'bottom': tbot,
               'right':RIGHT, 'top': ttop,
               'hspace': HSPACE, 'wspace': WSPACE}


def make_plot():
    df = read_csvs()
    df = df[df.is_selective]

    fig = mpl.figure(figsize=(FIG_WIDTH_FULL, 4), dpi=200)

    regions = ('A', 'PHC', 'H', 'HRipp')
    stages = 'WR3'

    grid = GridSpec(3, len(regions), **pos_dict_A)
    title_pos_y = 1.4
    for ireg, reg in enumerate(regions):
        for istage, stage in enumerate(stages):
            idx = (df.Region == reg) & (df.stage == stage) & (df.significant)
            if not idx.any():
                continue
            df_reg = df[idx].copy()

            plot = fig.add_subplot(grid[istage, ireg])
            prepare_plot(plot)
            # to_numpy gives a read-only view here, the original wrote into it
            x = df_reg.stim_dist.to_numpy(copy=True)
            neg_idx = x < 0
            x[neg_idx] = -1 * x[neg_idx]
            y = df_reg.x_peak.to_numpy(copy=True)
            y[neg_idx] = -1 * y[neg_idx]
            res = scipy.stats.pearsonr(x, y)
            print(f'Significant pairs (n = {x.shape[0]})', reg, stage, res)
            plot.scatter(x, y, 4, color=STAGE_COLORS[stage])
            m, b = np.polyfit(x, y, 1)
            xline = np.arange(-2, 12)
            plot.plot(xline, m*xline + b, color='grey', lw=.9)
            plot.text(0.05, .97,
                    f'N = {x.shape[0]} rho = {res.statistic:.3f} '
                    f'({pstars(res.pvalue, region=LONGNAMES[reg],
                               stage=STAGE_LONGNAMES[stage],
                               comparison='stimulus distance vs peak time',
                               test='pearsonr', alternative='two-sided',
                               n1=x.shape[0], statistic=res.statistic)})',
                            transform=plot.transAxes, va='bottom')
            plot.set_ylim((-150, 150))
            plot.set_yticks((-100, 0, 100))
            plot.set_xticks(range(1, 10))
            plot.set_xlim((0, 10))

            if istage == 0:
                plot.text(.5, title_pos_y, LONGNAMES[reg],
                            size=FONT_SIZE_REGIONS,
                            va='bottom', ha='center',
                            transform=plot.transAxes,
                            weight='bold')

            if (ireg, istage) == (0, 2):
                plot.text(-.3, .5, 'Peak time [ms]',
                            transform=plot.transAxes, va='center', ha='center',
                            rotation=90)
                plot.text(.5, -.5, 'Stimulus distance', ha='center',
                            transform=plot.transAxes)


        if ireg == 0:
            for stage in stages:
                plot.plot(-10, 1, color=STAGE_COLORS[stage],
                                lw=LW_LINE*1.1,
                                label=STAGE_LONGNAMES[stage])
                plot.legend(loc='lower left',
                        bbox_to_anchor=(-.2, -1.1),
                        ncol=3)

    pvalue_log.write('fig_S_12')
    save_figure(fig, 'fig_S_12', dpi=200)


if __name__ == '__main__':
    set_paper_style()
    with pvalue_log.context(figure='fig_S_12'):
        make_plot()
