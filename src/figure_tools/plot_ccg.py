"""
Cross-correlograms of unit pairs: sample correlograms and their asymmetry.
"""
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec
from matplotlib.transforms import blended_transform_factory
from scipy.stats import mannwhitneyu

from figure_tools.ccg_data import load_ccg_example
from figure_tools.plot_stats import label_diff, pstars
from figure_tools.style import (flierprops, STAGE_COLORS, STAGE_COLORS_PALE_2,
                                STAGE_LONGNAMES)

# the two sample jobs of panel A, as swr_name -> stages drawn
SAMPLE_JOBS = {'no': 'WR3', 'first': 'W3'}


def prepare_plot(plot):
    for position in ('top', 'right'):
        plot.spines[position].set_visible(False)
        plot.yaxis.grid(True)
        plot.set_axisbelow(True)


def plot_example(plots, example, swr_name, stage_iterator):

    width = example[f'{swr_name}_width']
    maxlag = example[f'{swr_name}_maxlag']
    xaxis = np.arange(-maxlag, maxlag + width, width)[:-1]

    for istage, stage in enumerate(stage_iterator):
        plot = plots[istage]
        plot.set_xlabel('Lag [ms]')

        peak = example[f'{swr_name}_{stage}_peak']
        n_neg = example[f'{swr_name}_{stage}_n_neg']
        n_pos = example[f'{swr_name}_{stage}_n_pos']
        tdata = example[f'{swr_name}_{stage}_hist']

        plot.bar(xaxis, tdata, width=width, edgecolor='none',
            facecolor=STAGE_COLORS_PALE_2[stage], align='edge')

        plot.axvline(0, color='k', ls='--', lw=.5)

        plot.set_xlim((xaxis[0], xaxis[-1]))

        fill = n_pos + n_neg
        asym = np.abs((n_pos - n_neg))/fill
        if (peak < 0) and (n_pos > n_neg):
            asym *= -1

        if swr_name == 'no':
            ripptext = '(all)'
        else:
            ripptext = '(only ripples)'
        text1 = '{} {}\n'.format(STAGE_LONGNAMES[stage], ripptext)
        text2 = '\nAsymmetry {:.3f}'.format(asym)
        for text, weight in ((text1, 'bold'), (text2, None)):
            plot.text(.5, 1.1, text, color='k',
                    transform=plot.transAxes, ha='center',
                    va='bottom', weight=weight)

        yticks = plot.get_yticks()
        if 2.5 in yticks:
            plot.set_yticks([0, 5])


def plot_A(fig, pos_dict):
    """
    plots examples of cross correlograms

    `pos_dict` has to have keys `left`, `bottom`, `right`, `top`
    """

    grid = GridSpec(1, 5, **pos_dict)

    example = load_ccg_example()

    for ijob, (swr_name, plot_stages) in enumerate(SAMPLE_JOBS.items()):

        plots = [fig.add_subplot(grid[i + 3 * ijob])
                for i in range(len(plot_stages))]

        plot_example(plots, example, swr_name, plot_stages)

        if ijob == 0:
            plots[0].set_ylabel('N')


def plot_asymmetry(plot, asym_data, stages, box_xs, pairs):

    boxes = plot.boxplot(asym_data, notch=True,
            patch_artist=True,
            flierprops=flierprops, positions=box_xs,
            widths=len(stages)/3*.4)

    plot.set_xticklabels([])
    transform = blended_transform_factory(plot.transData,
            plot.transAxes)

    stats = dict()

    all_rows = []

    for box_x, box, box_content, stage in zip(box_xs,
            boxes['boxes'], asym_data, stages):

        box.set_facecolor(STAGE_COLORS_PALE_2[stage])

        text = '{}\n{:.4f}'.format(box_content.shape[0],
                box_content.mean())

        plot.text(box_x, 1.05, text,
                color=STAGE_COLORS[stage],
                ha='center',
                transform=transform)

    for p1, p2 in pairs:
        x1 = stages.index(p1)
        x2 = stages.index(p2)

        if (p1, p2) == ('W', '3'):
            y = .85
        else:
            y = .65

        U, pval = mannwhitneyu(asym_data[x1],
                asym_data[x2], alternative='two-sided')

        row = [STAGE_LONGNAMES[p1], STAGE_LONGNAMES[p2],
                asym_data[x1].shape[0],
                asym_data[x2].shape[0], U, pval]
        all_rows.append(row)

        stats[(p1, p2, 'pval')] = pval

        label_diff(plot, transform, x1, x2, y, pstars(pval,
                comparison=f'{STAGE_LONGNAMES[p1]} vs {STAGE_LONGNAMES[p2]}',
                test='mannwhitneyu', alternative='two-sided',
                n1=asym_data[x1].shape[0], n2=asym_data[x2].shape[0],
                statistic=U), move_inner=.05)

    columns = ['Stage 1', 'Stage 2', 'N1', 'N2', 'U', 'p (Mann Whitney)']
    dataframe = pd.DataFrame(all_rows, columns=columns)

    return stats, dataframe
