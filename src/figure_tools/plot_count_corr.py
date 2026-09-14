from itertools import product

import numpy as np
import scipy.stats
from matplotlib.dates import date2num, DateFormatter, HourLocator
from matplotlib.gridspec import GridSpecFromSubplotSpec
from matplotlib.patches import Rectangle
from matplotlib.transforms import blended_transform_factory

from figure_tools.count_corr_data import load_cc_timecourse
from figure_tools import pvalue_log
from figure_tools.plot_stats import label_diff, pstars
from figure_tools.session_information import read_session_info
from figure_tools.style import (flierprops, STAGE_COLORS, STAGE_LONGNAMES,
                                TYPE_COLORS, TYPE_LETTERS, TYPE_NAMES)
from figure_tools.tools_fig_02 import COLOR_LINES, nlx_to_mpl, STAGEDICT

BOX_WIDTH = .4

# panel A, the sample session
TIMECOURSE_SESSION = (704, 1)


def plot_cc(ax, fid, groups, label_pairs, stages, add_ripple_label, options=None):
    if options is None:
        options = {'rsc_label_xpos': -.3}
    stars_weight = 'normal'

    fr_dict = dict()
    cc_dict = dict()

    for g, stg in product(groups, stages):
        data_temp = fid[f'cc_hemi_{g}_{stg}']
        idx = ~np.isnan(data_temp)
        data_temp = data_temp[idx]
        cc_dict[(g, stg)] = data_temp
        data_temp = fid[f'fr_hemi_{g}_{stg}']
        fr_dict[(g, stg)] = data_temp[idx]

    # print the firing rate comparison
    for stg in stages:
        for pair in label_pairs:
            g1, g2 = pair
            f1 = fr_dict[(g1, stg)]
            f2 = fr_dict[(g2, stg)]

            U, P = scipy.stats.mannwhitneyu(f1, f2)
            pvalue_log.record(P, stage=STAGE_LONGNAMES[stg],
                    comparison=f'firing rate, {g1} vs {g2}',
                    test='mannwhitneyu', alternative='two-sided',
                    n1=f1.shape[0], n2=f2.shape[0], statistic=U, drawn=False)
            print(stg, g1, g2, f'P firing: P_mannwh={P:.4f} rate1={f1.mean():.4g} vs. rate2={f2.mean():.4g}')

    xs = np.arange(len(groups))
    transform = blended_transform_factory(ax.transData, ax.transAxes)
    ax.yaxis.grid(True)

    for pos in ('top', 'right'):
        ax.spines[pos].set_visible(False)

    ax.text(options['rsc_label_xpos'], .5, r'$r_{\mathrm{SC}}$', ha='right',
                va='center', rotation=90, transform=ax.transAxes)

    ax.set_xlim((-.5, len(groups) * len(stages) - .5))
    gtypes = []
    for ilabel, label in enumerate(ax.get_xticklabels()):
        g = groups[ilabel % len(groups)]
        gtypes.append(g)
        label.set_color(TYPE_COLORS[g])

    for pos in range(1, len(groups)):
        ax.axvline(len(groups) * pos - .5, color='grey', lw=1)

    for istg, stg in enumerate(stages):
        text = STAGE_LONGNAMES[stg]

        if add_ripple_label:
            text = text + '\nripples'
        ax.text((istg + .5)* len(groups) - .5, -.12, text,
                    color=STAGE_COLORS[stg],
                    weight='bold', ha='center',
                    va='top', transform=transform)

        cc_data_list = [cc_dict[(g, stg)] for g in groups]
        boxes = ax.boxplot(cc_data_list, positions=istg * len(groups) + xs,
                   notch=True,
                   patch_artist=True,
                   flierprops=flierprops,
                   widths=BOX_WIDTH)

        for box, gtype in zip(boxes['boxes'], gtypes):
            color = TYPE_COLORS[gtype]
            box.set_facecolor(color)

        # individual stars above each data block
        for idata, g in enumerate(groups):
            data = cc_dict[(g, stg)]
            U, pval = scipy.stats.wilcoxon(data)
            print(f'{stg} {g} comparison to 0: P = {pval:.3g}')

            texts = (data.shape[0], f'{data.mean():.3f}',
                pstars(pval, stage=STAGE_LONGNAMES[stg], neuron_class=g,
                       comparison='against 0', test='wilcoxon',
                       alternative='two-sided', n1=data.shape[0],
                       statistic=U))

            for itext, text in enumerate(texts):
                ax.text(istg * len(groups) + idata, 1.12 - itext/20,
                        text, transform=transform,
                        ha='center', va='center',
                        weight=stars_weight)


        # now the comparisons
        for ipair, pair in enumerate(label_pairs):
            g1, g2 = pair
            U, pval = scipy.stats.mannwhitneyu(cc_dict[(g1, stg)], cc_dict[(g2, stg)])
            print(f'{stg} {g1} {g2} P count-corr = {pval:.4g}')
            # add the label diff
            x1 = groups.index(g1)
            x2 = groups.index(g2)
            label_diff(ax, transform, istg*len(groups) + x1, istg*len(groups) + x2,
                       .85 + ipair/20, pstars(pval, stage=STAGE_LONGNAMES[stg],
                           comparison=f'{g1} vs {g2}', test='mannwhitneyu',
                           alternative='two-sided',
                           n1=cc_dict[(g1, stg)].shape[0],
                           n2=cc_dict[(g2, stg)].shape[0], statistic=U))
    # some outer text
    texts = ('N =', 'mean =')
    for itext, text in enumerate(texts):
        ax.text(-.5, 1.12 - itext/20, text, va='center',
            ha='right', transform=transform)

    ax.set_xticks(np.arange(len(groups) * len(stages)))
    ax.set_xticklabels([TYPE_LETTERS[cl] for cl in groups] * len(stages))


def plot_hypnogram(plot, info):
    mpl_start = date2num(info.start_datetime)

    all_stages = info.sleepstages

    plot_starts = nlx_to_mpl(all_stages['starttime'],
                             info.start_nlx, mpl_start)
    plot_stops = nlx_to_mpl(all_stages['stoptime'],
                            info.start_nlx, mpl_start)

    xaxis_start = nlx_to_mpl(info.continuous_start,
                             info.start_nlx, mpl_start)
    xaxis_stop = nlx_to_mpl(info.continuous_stop,
                             info.start_nlx, mpl_start)

    timeaxis = np.vstack((plot_starts, plot_stops)).T.ravel()
    stageaxis = np.zeros((all_stages.shape[0], 2), int)

    for key in STAGEDICT:
        if key == '?':
            continue
        else:
            value = STAGEDICT[key]
        stageaxis[all_stages['stage'] == key, :] = (value, value)

    stageaxis = stageaxis.ravel()

    plot.plot(timeaxis, stageaxis, color=COLOR_LINES, lw=.7)
    plot.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    plot.set_xlim((xaxis_start, xaxis_stop))

    # do the REM in bold
    for i, row in enumerate(all_stages['stage']):
        if row == 'R':
            rect = Rectangle((plot_starts[i].item(), STAGEDICT['R']),
                             plot_stops[i].item() - plot_starts[i].item(), .3,
                             fc=COLOR_LINES, edgecolor='none')
            plot.add_artist(rect)

    # this ylim controls how much the gap between
    # A and B is filled with text
    plot.set_ylim((-3.5, 1.5))
    plot.set_yticks((-3, -2, -1, 0, 1))
    plot.set_yticklabels(('3', '2', '1', 'R', 'W'))
    plot.set_xticklabels([])

    for pos in ('top', 'right', 'bottom'):
        plot.spines[pos].set_visible(False)


def plot_E(plot, info, timecourse, inv_classes):
    """
    plot sample time course of r_SC
    """

    for pos in ('top', 'right'):
        plot.spines[pos].set_visible(False)

    mpl_start = date2num(info.start_datetime)

    plot_starts = nlx_to_mpl(timecourse['bins'][:, 0],
                             info.start_nlx, mpl_start)

    xaxis_start = nlx_to_mpl(info.continuous_start,
                             info.start_nlx, mpl_start)
    xaxis_stop = nlx_to_mpl(info.continuous_stop,
                             info.start_nlx, mpl_start)
    plot.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    plot.set_xlim((xaxis_start, xaxis_stop))
    plot.set_xlabel('Time of day')

    for icl, cl in enumerate(inv_classes):
        m_data = timecourse[cl]
        label = '{}, {}'.format(TYPE_LETTERS[cl], TYPE_NAMES[cl].capitalize())
        plot.plot(plot_starts, m_data, color=TYPE_COLORS[cl], lw=1,
                label=label, zorder=-1*icl)

    for tick in plot.get_xticks():
        plot.axvline(tick, color='grey', zorder=0, clip_on=False,
                ymin=0, ymax=2.1, lw=.5)

    lgd = plot.legend(loc='lower left', bbox_to_anchor=(-.15, -1.5))
    texts = lgd.get_texts()
    for text, cl in zip(texts, inv_classes):
        text.set_color(TYPE_COLORS[cl])


def plot_timecourse(fig, grid):
    inv_classes = ('no_resp', 'inv')
    info = read_session_info(*TIMECOURSE_SESSION)
    timecourse = load_cc_timecourse()
    E_plots = GridSpecFromSubplotSpec(3, 1, grid[0, :2],
            height_ratios=[3, 3, 2])
    plot_hypno = fig.add_subplot(E_plots[0])
    plot_corr = fig.add_subplot(E_plots[1])

    locator = HourLocator(interval=2)
    for p, text in ((plot_hypno, 'Sleep stage'),
            (plot_corr, r'$r_{\mathrm{SC}}$')):
        p.xaxis.set_major_locator(locator)

        p.text(-.12, .5, text, rotation=90,
                ha='right', va='center', transform=p.transAxes)

    plot_hypno.set_xticks([])
    plot_hypnogram(plot_hypno, info)
    plot_E(plot_corr, info, timecourse, inv_classes)
