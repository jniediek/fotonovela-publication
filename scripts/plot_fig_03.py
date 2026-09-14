import matplotlib.pyplot as mpl
from matplotlib.gridspec import GridSpec
from matplotlib.transforms import blended_transform_factory
from scipy.stats import mannwhitneyu, wilcoxon

from figure_tools.definitions import (FIG_WIDTH_FULL,
                                      FONT_SIZE_REGIONS, LONGNAMES)
from figure_tools.plot_stats import label_diff, pstars
from figure_tools.population import load_population
from figure_tools import pvalue_log
from figure_tools.recall_data import load_recall
from figure_tools.style import (flierprops, save_figure, set_paper_style, TYPE_COLORS,
                                TYPE_LETTERS, TYPE_NAMES)

flierprops['markersize'] = 1.5
BOX_WIDTH = .4


def make_plot_one_region(plot, df, reg, do_annotation):

    # JN 2023-07-11 this is the `is_consistent` property
    df = df[df.stim_order_quality > 0].copy()
    print(f'Starting plot {reg}, {df.shape}')

    if do_annotation:
        tstr = 'Firing during recall\n(normalized)'
        plot.text(-.2, .5, tstr, va='center', ha='center', rotation=90,
                transform=plot.transAxes)

    blended_tansform = blended_transform_factory(plot.transData,
            plot.transAxes)

    groups = ('inv_self', 'inv_other', 'resp_self', 'resp_other')
    colors = ('inv', 'inv', 'resp', 'resp', 'no_resp')
    other_self = ('-P', '-NP', '-P', '-NP', '')
    resp_labels = {'-P': 'preferred stimuli',
            '-NP': 'non-preferred stimuli',
            '': ''}
    alphas = (1, .5, 1, .5, 1)
    plot_data = []

    # this is the name of the region
    plot.text(.5, 1.5, LONGNAMES[reg], weight='bold',
            size=FONT_SIZE_REGIONS, va='bottom', ha='center',
            transform=plot.transAxes)

    for name in groups:

        if 'resp' in name:
                idx = df.is_selective
                print('After selective reduction', name, idx.sum())

        if 'inv' in name:
                idx = df.is_inv

        if 'self' in name:
                idx_sel = df.preferred_stim_num == df['Stim-Num']
                idx = idx & idx_sel

        if 'other' in name:
                sel_idx = df.preferred_stim_num != df['Stim-Num']
                idx = idx & sel_idx

        print(name, idx.sum())
        plot_data.append(df.recall_selectivity[idx].dropna())

    xaxis = [0, .8, 2, 2.8] #, 4]

    boxes = plot.boxplot(plot_data, notch=True, patch_artist=True,
            positions=xaxis, flierprops=flierprops, widths=BOX_WIDTH)

    for dataset, pos, label, pnp, alpha, group in zip(plot_data, xaxis, colors,
            other_self, alphas, groups):

        # this is the relevant information
        N = dataset.dropna().shape[0]
        t_mean = dataset.dropna().mean()
        T, p = wilcoxon(dataset.dropna())
        tstr = '{}\n{:.2f}\n{}'.format(N, t_mean, pstars(p, group=group,
            comparison='against 0', test='wilcoxon', alternative='two-sided',
            n1=N, statistic=T))
        # print('z > 0: {} {} units'.format(label, (dataset.dropna() > 0).sum()))
        print(f'Avg. z = {t_mean:.03f} P for zscores for {label} {group} group: {p:.3g}')
        plot.text(pos, 1.1, tstr, ha='center', va='bottom', transform=
                blended_tansform)
                # this is the tick labeling
        plot.text(pos, -.2,
                TYPE_LETTERS[label] + pnp,
                va='center', ha='center', transform=blended_tansform,
                color=TYPE_COLORS[label], alpha=alpha)

        # this is for the legend:
        legend_label = (TYPE_LETTERS[label] + pnp + ', ' +
                TYPE_NAMES[label].capitalize())
        if label != 'no_resp':
            legend_label += '\n' + resp_labels[pnp]
        plot.plot(-4, -4, color=TYPE_COLORS[label], alpha=alpha,
                label=legend_label)


    # these are the group comparisons:
    index_pairs = ((0, 1), # CP vs CNP
                   (2, 3), # RP vs RNP
                   (0, 2)) # CP vs RP

    ypos = (.8, .82, 1)
    for (p1, p2), pos in zip(index_pairs, ypos):
        dset1 = plot_data[p1].dropna()
        dset2 = plot_data[p2].dropna()
        U, p = mannwhitneyu(dset1, dset2)
        label_diff(plot, blended_tansform, xaxis[p1] + .05,
                xaxis[p2] - .05,
                pos, pstars(p, comparison=f'{groups[p1]} vs {groups[p2]}',
                    test='mannwhitneyu', alternative='two-sided',
                    n1=dset1.shape[0], n2=dset2.shape[0], statistic=U))
        print('Comparing z scores', groups[p1], groups[p2], f'P value = {p:.3g}')

    for ibox, box in enumerate(boxes['boxes']):
        box.set_facecolor(TYPE_COLORS[colors[ibox]])
        box.set_alpha(alphas[ibox])


    if do_annotation:
        # this is the information label
        tstr = 'N =\nMean(z) =\n'
        plot.text(0, 1.1, tstr, ha='right', va='bottom', transform=
                plot.transAxes)

        # this is the legend
        lgd = plot.legend(loc='upper left', bbox_to_anchor=(-.3, -.3),
                ncol=3)
        texts = lgd.get_texts()
        for label, text, alpha in zip(colors, texts, alphas):
            text.set_color(TYPE_COLORS[label])
            text.set_alpha(alpha)


    plot.set_xlim((-.5, len(groups) - .6))
    plot.set_ylim((-4, 5))
    plot.set_xticklabels([])
    plot.yaxis.grid(True)
    for pos in ('top', 'right'):
        plot.spines[pos].set_visible(False)


def main():
    regs = ('A', 'H', 'PHC')

    df = load_recall()

    pop = load_population()
    for reg in regs:
        idx = (pop.Simple_Region == reg) & (pop.is_inv) & (pop.is_consistent)
        print(f'In population: {reg} #inv = {idx.sum()}')


    df = df.merge(pop[['ident', 'preferred_stim_num', 'is_inv', 'is_selective',
                       'stim_order_quality', 'Region', 'Simple_Region']], on='ident', validate='m:1')

    for reg in regs:
        idx = (df.Simple_Region == reg) & (df.is_inv)
        print(f'In responses: {reg} #inv = {idx.sum()}')

    fig = mpl.figure(figsize=(FIG_WIDTH_FULL, 5), dpi=300, facecolor='w')

    # boxplot grid
    LEFT = .1
    RIGHT = .97
    bottom_A = .35
    top_A = .72
    grid_boxplot = GridSpec(1, 3, left=LEFT, bottom=bottom_A, right=RIGHT,
            top=top_A)

    for ireg, reg in enumerate(regs):
        plot = fig.add_subplot(grid_boxplot[ireg])
        reg_frame = df[df.Simple_Region == reg]
        print(reg)
        with pvalue_log.context(figure='fig_03', region=LONGNAMES[reg]):
            make_plot_one_region(plot, reg_frame, reg, ireg==0)

    pvalue_log.write('fig_03')
    save_figure(fig, 'fig_03')
    mpl.close(fig)


if __name__ == "__main__":
    set_paper_style()
    main()