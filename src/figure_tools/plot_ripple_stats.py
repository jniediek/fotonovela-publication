import numpy as np
import pandas as pd
import scipy.stats
from matplotlib import rcParams
from matplotlib.transforms import blended_transform_factory
from scipy.stats import mannwhitneyu

from figure_tools.plot_stats import label_diff, pstars
from figure_tools.style import (flierprops, STAGE_COLORS, STAGE_COLORS_PALE_2,
                                STAGE_LONGNAMES, TYPE_COLORS, TYPE_LETTERS)
from figure_tools.tools_fig_02 import COLOR_LINES

BIN_WIDTH = 25
T_PRE = 375
T_POST = 375
HIST_BINS = np.arange(-T_PRE, T_POST + BIN_WIDTH, BIN_WIDTH)

STAGES = ('W', 'R', '3')

# this is for all boxplots here
flierprops['markersize'] = 1.5
BOX_WIDTH = .4


def create_raster_data(unit, frame):

    good_idx = (~frame.Time_overlap &
                ~frame.Amplitude_high &
                frame.Freq_domain.isin((1, 2)) &
                (frame.Stage.isin(('W', '3'))))

    swr_times = frame.loc[good_idx, 'Centertime'].dropna().values
    unit_times = unit['times']
    row_data = []

    hist_data = []

    for swr_time in swr_times:
        start = unit_times.searchsorted(swr_time - T_PRE)
        stop = unit_times.searchsorted(swr_time + T_POST)
        if stop != start:
            trow = unit_times[start:stop] - swr_time
            row_data.append(trow)
            hist_row, _ = np.histogram(trow, HIST_BINS)
            hist_data.append(hist_row*1000/BIN_WIDTH)

    # transform to histogram
    histogram = np.array(hist_data).mean(0)

    return row_data, histogram


def plot_ripple_rates(fig, pos, frame):
    """
    B shows sleep-stage dependent hippocampal ripple rates
    """
    target_data = 'Rate'
    frame = frame.dropna()

    plot_data = []
    plot_data_dict = {}
    rows_comp = []
    rows_data = []

    plot = fig.add_subplot(pos)
    for pos in ('top', 'right'):
        plot.spines[pos].set_visible(False)
    trans = blended_transform_factory(plot.transData, plot.transAxes)

    xaxis = (0, 1, 2)
    plot.set_xlim((-.5, 2.5))
    plot.set_ylim((-.01, .59))
    plot.set_ylabel('Ripple rates [Hz]')

    for istage, stage in enumerate(STAGES):
        idx = frame.Stage == stage
        data = frame.loc[idx, target_data].dropna().to_numpy()

        plot_data.append(data)
        plot_data_dict[stage] = data
        plot.text(xaxis[istage], 1.12, str(data.shape[0]), va='center',
                ha='center', color=STAGE_COLORS[stage], transform=trans)
        plot.text(xaxis[istage], 1.07, '{:.2f}'.format(data.mean()),
                va='center', ha='center', color=STAGE_COLORS[stage],
                transform=trans)
        this_row = [STAGE_LONGNAMES[stage], data.shape[0], np.median(data),
                 np.quantile(data, .25), np.quantile(data, .75)]
        rows_data.append(this_row)


    for (st, x1, y) in zip('W3', [0, 1], [.9, 1]):
        x2 = x1 + 1
        U, p = mannwhitneyu(plot_data_dict['R'], plot_data_dict[st],
                alternative='two-sided')
        label_diff(plot, trans, x1, x2, y, pstars(p,
                comparison=f"{STAGE_LONGNAMES['R']} vs {STAGE_LONGNAMES[st]}",
                test='mannwhitneyu', alternative='two-sided',
                n1=plot_data_dict['R'].shape[0],
                n2=plot_data_dict[st].shape[0], statistic=U))
        this_row = [STAGE_LONGNAMES['R'], STAGE_LONGNAMES[st], U, p]
        rows_comp.append(this_row)

    cols_data = ['Stage', 'N', 'Median', 'Q1', 'Q3']
    cols_comp = ['Stage 1', 'Stage 2', 'U', 'p (Mann Whitney)']
    fr1 = pd.DataFrame(rows_data, columns=cols_data)
    # fr1.to_csv('results_ripple_rates.csv')
    fr2 = pd.DataFrame(rows_comp, columns=cols_comp)
    # fr2.to_csv('results_ripple_rates_comparison.csv')

    print(fr1)
    print(fr2)

    boxes = plot.boxplot(plot_data, notch=True, patch_artist=True,
            positions=xaxis, flierprops=flierprops, widths=BOX_WIDTH)

    for box, color in zip(boxes['boxes'],
            [STAGE_COLORS_PALE_2[st] for st in STAGES]):
        box.set_facecolor(color)

    plot.set_xticklabels([STAGE_LONGNAMES[st] for st in STAGES],
        rotation=90, weight='bold')


    for label, color in zip(plot.get_xticklabels(),
                            [STAGE_COLORS[st] for st in STAGES]):
        label.set_color(color)

    plot.yaxis.grid(True)

    texts = (u'N =', u'mean =')
    for itext, text in enumerate(texts):
        plot.text(-.5, 1.12 - itext/20, text, va='center',
                  ha='right', transform=trans)

    return fr1, fr2


def plot_ripple_frequencies(plot, frame):
    STAGES = 'W3'
    target_data = 'MeanFreq'
    for pos in ('top', 'right'):
        plot.spines[pos].set_visible(False)
    trans = blended_transform_factory(plot.transData, plot.transAxes)

    xaxis = list(range(len(STAGES)))
    plot.set_xlim((-.5, xaxis[-1] + .5))
    plot.set_ylim((45, 160))

    plot_data = []
    plot_data_dict = {}

    frame = frame.dropna()

    for istage, stage in enumerate(STAGES):
        idx = frame.Stage == stage
        data = frame.loc[idx, target_data].dropna().to_numpy()

        plot_data.append(data)
        plot_data_dict[stage] = data
        plot.text(xaxis[istage], 1.12, str(data.shape[0]), va='center',
                ha='center', color=STAGE_COLORS[stage], transform=trans)
        plot.text(xaxis[istage], 1.07, '{:.2f}'.format(data.mean()),
                va='center', ha='center', color=STAGE_COLORS[stage],
                transform=trans)

    U, p = mannwhitneyu(plot_data_dict['W'], plot_data_dict['3'],
                        alternative='two-sided')
    label_diff(plot, trans, 0, 1, .9, pstars(p,
            comparison=f"{STAGE_LONGNAMES['W']} vs {STAGE_LONGNAMES['3']}",
            test='mannwhitneyu', alternative='two-sided',
            n1=plot_data_dict['W'].shape[0],
            n2=plot_data_dict['3'].shape[0], statistic=U))

    boxes = plot.boxplot(plot_data, notch=True, patch_artist=True,
            positions=xaxis, flierprops=flierprops, widths=BOX_WIDTH)

    for box, color in zip(boxes['boxes'],
            [STAGE_COLORS_PALE_2[st] for st in STAGES]):
        box.set_facecolor(color)

    plot.set_xticklabels([STAGE_LONGNAMES[st] for st in STAGES],
        rotation=90, weight='bold')


    for label, color in zip(plot.get_xticklabels(),
                            [STAGE_COLORS[st] for st in STAGES]):
        label.set_color(color)

    plot.yaxis.grid(True)

    texts = (u'N =', u'mean =')
    for itext, text in enumerate(texts):
        plot.text(-.5, 1.12 - itext/20, text, va='center',
                  ha='right', transform=trans)


def plot_swr_raster(plot_raster, plot_hist, raster, histogram):

    plot_raster.eventplot(raster, color=[COLOR_LINES]*len(raster), linewidths=.5,
                          rasterized=True)
    plot_hist.bar(HIST_BINS[:-1], histogram, width=BIN_WIDTH,
                  ec='none', fc=COLOR_LINES, align='edge')
    for p, t in ((plot_raster, 'Counts'), (plot_hist, 'f [Hz]')):
        p.text(-.25, .5, t, transform=p.transAxes, rotation=90, ha='right', va='center')
        p.set_xlim((-T_PRE, T_POST))


def plot_ripple_binding(plot, binding_data, plot_classes: list, do_labels=True):

    STAGES = ('W', '3')

    all_pvals = dict()

    for pos in ['top', 'right']:
        plot.spines[pos].set_visible(False)

    plot.set_ylabel(u'Effect size (Cohen’s d)')
    plot.set_ylim((-.2, 1.15))

    transform = blended_transform_factory(plot.transData, plot.transAxes)

    n_plot_classes = len(plot_classes)
    xshift = n_plot_classes
    xaxis = np.arange(n_plot_classes)

    for i_outer, stage in enumerate(STAGES):

        stage_data = []

        if i_outer == 0:
            texts = (u'N =', r'$\overline{\mathrm{d}}$ =', '')
            for itext, text in enumerate(texts):
                plot.text(-.5, 1.12 - itext/20, text, va='center',
                        ha='right', transform=transform)

        for i_inner, resp_type in enumerate(plot_classes):
            # data_pre = hedges_g[stage][idxs_resp[resp_type]].dropna()
            # data = data_pre.values
            data = binding_data[f'cohen_{resp_type}_{stage}']
            stage_data.append(data)

            # add stars for the group
            T, pval = scipy.stats.wilcoxon(data)

            this_pval_name = '{}_{}_Hedge_Wilcoxon'.format(stage,
                    resp_type)
            all_pvals[this_pval_name] = pval

            texts = (f'{data.shape[0]}',
                     f'{data.mean():.2f}',
                     pstars(pval, stage=STAGE_LONGNAMES[stage],
                            neuron_class=resp_type, comparison='against 0',
                            test='wilcoxon', alternative='two-sided',
                            n1=data.shape[0], statistic=T))

            weight = ('normal', 'normal', 'bold')
            for itext, (text, weight) in enumerate(zip(texts, weight)):
                size = rcParams['font.size'] = 7
                ypos = 1.12 - itext/20
                if '*' in text:
                    ypos = ypos - .02
                    size *= 1.5
                plot.text(i_outer * xshift + i_inner,
                          ypos, text,
                          transform=transform,
                          color=TYPE_COLORS[resp_type],
                          ha='center', va='center',
                          weight=weight, fontsize=size)

        boxes = plot.boxplot(stage_data,
                    positions=xaxis + i_outer * xshift, notch=True,
                    patch_artist = True, flierprops=flierprops,
                    widths=BOX_WIDTH)

        for box, color in zip(boxes['boxes'],
                [TYPE_COLORS[cl] for cl in plot_classes]):
            box.set_facecolor(color)

        plot.text(i_outer * xshift + (xshift-1)/2, -.12,
            u'{}\nripples'.format(STAGE_LONGNAMES[stage]),
            color=STAGE_COLORS[stage],
            weight='bold', ha='center', transform=transform, va='top')

    # add comparison between stages
    if do_labels:
        pairs = (('cohen_inv_W', 'cohen_inv_3'), ('cohen_resp_W', 'cohen_resp_3'))
        pos = ((0, xshift), (1, xshift + 1))
        for pair, tpos in zip(pairs, pos):
            d1 = binding_data[pair[0]]
            d2 = binding_data[pair[1]]
            U, pval = scipy.stats.mannwhitneyu(d1, d2)
            print(f'Comparing {pair[0]} to {pair[1]} P = {pval:.4g}')
            label_diff(plot, transform, tpos[0], tpos[1], .85 + tpos[0]/12,
                    pstars(pval, comparison=f'{pair[0]} vs {pair[1]}',
                           test='mannwhitneyu', alternative='two-sided',
                           n1=d1.shape[0], n2=d2.shape[0], statistic=U))



    plot.set_xlim((-.5, len(plot_classes) * len(STAGES) - .5))
    plot.set_xticks(np.arange(len(plot_classes) * len(STAGES)))
    plot.set_xticklabels([TYPE_LETTERS[cl] for cl in plot_classes] * len(STAGES))
    plot.yaxis.grid(True)

    for ilabel, label in enumerate(plot.get_xticklabels()):
        label.set_color(TYPE_COLORS[plot_classes[ilabel % len(plot_classes)]])

    plot.axvline(len(plot_classes) - .5, color='grey', lw=1)

    return all_pvals
