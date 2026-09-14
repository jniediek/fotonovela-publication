from itertools import product
import scipy.stats
import matplotlib.pyplot as mpl
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec

from figure_tools.definitions import (FIG_WIDTH_FULL, FIGURE_DIR,
                                      FONT_SIZE_LETTERS)
from figure_tools.plot_ripple import plot_swr_event
from figure_tools.plot_ripple_stats import (create_raster_data,
                                            plot_ripple_binding,
                                            plot_ripple_rates,
                                            plot_swr_raster)
from figure_tools.ripple_data import (load_binding_data, load_swr_info,
                                      load_swr_rates)
from figure_tools import pvalue_log
from figure_tools.style import (save_figure, set_paper_style, STAGE_LONGNAMES,
                                TYPE_COLORS, TYPE_LETTERS, TYPE_NAMES)
from figure_tools.swr_data import load_swr_event
from figure_tools.unit_data import load_unit

# the sample event of panel A
SWR_EVENT = '712fn1_CSC30_swr_0935'

RASTER_UNITS = (('717fn2_CSC68_pos_01', (717, 2, 68)),
                ('716fn1_CSC12_pos_01', (716, 1, 12)))


def load_data_SWR():
    """
    read the necessary data
    returns: swr_event, rasters, histograms
    """
    # for A, SWR sample event
    swr_event = load_swr_event(SWR_EVENT)

    rasters = []
    histograms = []

    for name, (pat, ses, chan) in RASTER_UNITS:
        unit = load_unit(name)
        frame = load_swr_info(pat, ses, chan)
        ra, hi = create_raster_data(unit, frame)
        rasters.append(ra)
        histograms.append(hi)

    return swr_event, rasters, histograms


def do_plot(jobs: str, binding_data: dict):

    LGAP = .08
    BOTTOM = .15
    TOP = .85
    RIGHT = .98
    WSPACE = .7
    HSPACE = .5

    fig_1 = mpl.figure(figsize=(FIG_WIDTH_FULL, 3.2), dpi=200)

    grid_1 = GridSpec(1, 4, left=LGAP, bottom=BOTTOM+.11, right=RIGHT,
            top=TOP, wspace=WSPACE, hspace=HSPACE,
                    width_ratios=[4, 2.5, 3, 3])

    left_shift = .07
    top_shift = .1
    corr = 0.01

    _, tops, lefts, _ = grid_1.get_grid_positions(fig_1)

    letter_pos = [('A', fig_1, lefts[0], tops[0]),
                  ('B', fig_1, lefts[1], tops[0]),
                  ('C', fig_1, lefts[2], tops[0]),
                  ('D', fig_1, lefts[3] - corr, tops[0])]

    for letter, fig, x, y in letter_pos:
        fig.text(x - left_shift, y + top_shift,
                 letter.lower(), weight='bold', size=FONT_SIZE_LETTERS)

    rate_frame = load_swr_rates()

    if ('A' in jobs) or ('B' in jobs) or ('C' in jobs):
        swr_event, rasters, histograms = load_data_SWR()

    if 'A' in jobs:
        A_plot_pos = GridSpecFromSubplotSpec(3, 3, grid_1[0, 0], hspace=.1,
                wspace=.1, width_ratios=[76, 4, 20])
        A_plots = [fig_1.add_subplot(A_plot_pos[x, y]) for x, y in
                ((0, 0), (1, 0), (2, 0), (2, 1))]
        plot_swr_event(A_plots, swr_event, do_texts=True, do_texts_right=True)

    if 'B' in jobs:
        print('Starting panel B')
        with pvalue_log.context(figure='fig_05', panel='b'):
            df_data, df_compare = plot_ripple_rates(fig_1, grid_1[0, 1], rate_frame)
        df_data.to_csv(FIGURE_DIR / 'fig_05_results_ripple_rates.csv', index=False)
        df_compare.to_csv(FIGURE_DIR / 'fig_05_results_ripple_rates_comparison.csv',
                          index=False)

    if 'C' in jobs:
        C_plots = GridSpecFromSubplotSpec(4, 1, grid_1[0, 2])

        for i in (0, 1):
            plot_1 = fig_1.add_subplot(C_plots[2*i])
            plot_1.set_xticklabels([])
            plot_2 = fig_1.add_subplot(C_plots[2*i + 1])

            for p, pos in product((plot_1, plot_2), ('right', 'top')):
                p.spines[pos].set_visible(False)

            plot_1.spines['bottom'].set_visible(False)
            plot_1.set_xticks([])

            if i == 0:
                plot_2.set_xticklabels([])
            else:
                plot_2.set_xlabel('ms')

            print('Starting panel C')
            plot_swr_raster(plot_1, plot_2, rasters[i], histograms[i])

    if 'D' in jobs:
        D_plot_pos = GridSpecFromSubplotSpec(2, 1, grid_1[0, 3], hspace=0,
            wspace=0, height_ratios=[5, 1])

        D_plot = fig_1.add_subplot(D_plot_pos[:, 0])

        plot_classes = ['inv', 'resp']

        print('Starting panel D')
        with pvalue_log.context(figure='fig_05', panel='d'):
            plot_ripple_binding(D_plot, binding_data, plot_classes)

        D_legend_plot = fig_1.add_subplot(D_plot_pos[1, 0])

        D_legend_plot.axis('off')
        for cl in plot_classes:
            label = f'{TYPE_LETTERS[cl]}, {TYPE_NAMES[cl].capitalize()}'
            D_legend_plot.plot([0, 1], [0, 0], color=TYPE_COLORS[cl],
                    label=label)

        D_legend_plot.set_xlim((20, 21))

        lgd = D_legend_plot.legend(loc='lower left',
                bbox_to_anchor=(-.2, -2.6))

        texts = lgd.get_texts()
        for text, cl in zip(texts, plot_classes):
            text.set_color(TYPE_COLORS[cl])
    return fig_1


def do_stats(binding_data):
    # simply loop over stages and resp types
    for stage in ('W', '3'):
        for inv_class in ('inv', 'resp', 'no_resp'):
            key = f'cohen_{inv_class}_{stage}'
            data = binding_data[key]
            T, pval = scipy.stats.wilcoxon(data)
            pvalue_log.record(pval, stage=STAGE_LONGNAMES[stage],
                    neuron_class=inv_class, comparison='against 0',
                    test='wilcoxon', alternative='two-sided',
                    n1=data.shape[0], statistic=T)
            print(f'Stage {stage} neurons {inv_class} mean cohen = {data.mean():.4f} Pwilcx = {pval:.4g}')
            if inv_class != 'no_resp':
                key = f'cohen_no_resp_{stage}'
                d2 = binding_data[key]
                U, pval = scipy.stats.mannwhitneyu(data, d2, alternative='two-sided')
                pvalue_log.record(pval, stage=STAGE_LONGNAMES[stage],
                        comparison=f'{inv_class} vs no_resp',
                        test='mannwhitneyu', alternative='two-sided',
                        n1=data.shape[0], n2=d2.shape[0], statistic=U)
                print(f'Stage {stage} neurons {inv_class} vs no_resp Pmannw = {pval:.4g}')


def main():
    jobs = 'ABCD'
    binding_data = load_binding_data()
    fig = do_plot(jobs, binding_data)

    # do the stats
    with pvalue_log.context(figure='fig_05', drawn=False):
        do_stats(binding_data)

    pvalue_log.write('fig_05')
    save_figure(fig, 'fig_05', dpi=250, pdf_dpi=300)
    mpl.close(fig)


if __name__ == '__main__':
    set_paper_style()
    main()
