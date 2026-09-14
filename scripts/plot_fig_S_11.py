import numpy as np
import scipy.stats
import pandas as pd
import matplotlib.pyplot as mpl
from matplotlib.gridspec import GridSpec
from matplotlib.transforms import blended_transform_factory

from figure_tools.ccg_data import read_csvs_extra
from figure_tools.definitions import (FIG_WIDTH_FULL,
                                      FONT_SIZE_LETTERS, FONT_SIZE_REGIONS,
                                      LONGNAMES)
from figure_tools.plot_ccg import prepare_plot
from figure_tools.plot_stats import label_diff, pstars
from figure_tools import pvalue_log
from figure_tools.style import (flierprops, save_figure, set_paper_style, STAGE_COLORS,
                                STAGE_COLORS_PALE_2)

LEFT = .08
RIGHT = .98
HSPACE = .5
WSPACE = .5

ttop = .63
tbot = .09
c_shift = .03
modenames = {'asymmetry': 'Abs. asymmetry',
                'peak': 'Pairs [%]'}


spacing = (ttop - tbot)/5


pos_dict_B = {'left': LEFT, 'bottom': tbot+4*spacing,
            'right':RIGHT, 'top': ttop,
            'hspace': HSPACE, 'wspace': WSPACE}
modenames = {'asymmetry': 'Abs. asymmetry',
                    'peak': 'Pairs [%]'}


def get_data() -> pd.DataFrame:
    df = read_csvs_extra()
    df = df[df.is_selective].reset_index(drop=True)
    return df

hatches = {'1': None, '2': '//'}
labels = {'W1': 'Post-exp. 1h',
        'W2': 'Post-exp. 2h',
        '31': 'SWS first half',
        '32': 'SWS second half'}
def plot_decoding_panel_mod(data, timepoints, plot, plot_asym_shift):
    # also plot asymm. shifts between 31 and 32

    rem = data['x_peak'].abs() < 3
    data = data[~rem].copy().reset_index(drop=True)
    data.loc[:, 'coincident'] = np.sign(data['x_peak']) == np.sign(data['stim_dist'])

    width = .7

    data_dict = {}

    for istage, stage in enumerate(timepoints):
        idx = (data.timepoint == stage) & data['significant']
        t_data = data[idx]

        # print(t_data)
        n_total = t_data.shape[0]
        n_coincident = t_data['coincident'].sum()
        n_wrong = (~t_data['coincident']).sum()
        print(stage, n_total, n_coincident, n_wrong)

        temp1 = t_data.loc[:, ['ident_pairs', 'asymmetry', 'coincident']].copy()
        temp2 = temp1.copy()
        temp2.loc[~(temp2.coincident), 'asymmetry'] = -1 * temp2.loc[~(temp2.coincident), 'asymmetry']
        data_dict[stage] = temp2

        # to be sure that the sign inversion has happened
        # print(data_dict[stage].asymmetry - temp1.asymmetry)

        for val, bot, facecolor in ((n_coincident/n_total, 0, True),
                                    (n_wrong/n_total, n_coincident/n_total, False)):
            edgecolor = STAGE_COLORS_PALE_2[stage[0]]
            if facecolor:
                facecolor = edgecolor
                hatch = hatches[stage[1]]
            else:
                facecolor = 'w'
                hatch = None

            plot.bar(istage, 100*val, bottom=100*bot, width=width, align='center',
                     color='w', ec='k', fc=facecolor, hatch=hatch)

        for val, pos in ((n_coincident, 50), (n_wrong, 95)):
            plot.text(istage + width/2 + .02, pos, int(val), ha='left', va='center', weight='bold')

        if n_total == 0:
            continue
        binom_res = scipy.stats.binomtest(n_coincident, n_total, .5)

        plot.text(istage, 105, f'{n_coincident/n_total:.1%}\n '
                  f'{pstars(binom_res.pvalue, panel="c", timepoint=labels[stage],
                            comparison="forward vs reverse", test="binomtest",
                            alternative="two-sided", n1=n_coincident,
                            n2=n_wrong)}', ha='center',
                   va='bottom')

    d1 = data_dict['31']
    d2 = data_dict['32']

    # find the common index
    d1n = d1[d1.ident_pairs.isin(d2.ident_pairs)]
    d2n = d2[d2.ident_pairs.isin(d1.ident_pairs)]

    print(f'Reducing d1 from {d1.shape[0]} to {d1n.shape[0]}\nReducing d2 from {d2.shape[0]} to {d2n.shape[0]}')
    data = np.vstack((d1n.asymmetry.to_numpy(copy=True), d2n.asymmetry.to_numpy(copy=True)))

    plot_asym_shift.plot([0, 1], data, color='lightgrey', lw=.5, label=None)

    for i, st in enumerate(('31', '32')):
        plot_asym_shift.plot(i + np.zeros(d1n.shape[0]), data[i, :], marker='.',
                mfc=STAGE_COLORS[st], mec=STAGE_COLORS[st], lw=0,
                label=None)

    min_val = np.min((data[0].min(), data[1].min()))
    max_val = np.max((data[0].max(), data[1].max()))
    ylim = np.array((min_val, max_val)) * 1.2

    plot_asym_shift.set_xlim([-.5, 1.5])
    plot_asym_shift.set_ylim(ylim)

    plot_asym_shift.set_xticks([0, 1])

    res = scipy.stats.wilcoxon(data[0, :], data[1, :])
    transform = blended_transform_factory(plot_asym_shift.transData,
                                          plot_asym_shift.transAxes)
    label_diff(plot_asym_shift, transform, 0, 1, 1,
            pstars(res.pvalue, panel='b',
                   comparison=f'{labels["31"]} vs {labels["32"]}',
                   test='wilcoxon', alternative='two-sided',
                   n1=data.shape[1], statistic=res.statistic))


def plot_extra_information_phases(df):
    regions = ('A', 'PHC', 'H' )

    # bottom_mid = .5
    top = .859
    #bottom = .15
    #ttop = .5
    tbot = .062
    #c_shift = .03

    spacing = (top - tbot)/5


    pos_dict_A = {'left': LEFT, 'bottom': tbot + 4*spacing,
               'right': RIGHT, 'top': top, 'hspace': HSPACE, 'wspace': WSPACE}
    pos_dict_C = pos_dict_B = {'left': LEFT, 'bottom': tbot + 2*spacing,
               'right': RIGHT, 'top': tbot + 3*spacing, 'hspace': HSPACE, 'wspace': WSPACE}
    pos_dict_B = {'left': LEFT, 'bottom': tbot,
               'right': RIGHT, 'top': tbot + spacing, 'hspace': HSPACE, 'wspace': WSPACE}


    grid_A = GridSpec(1, len(regions), **pos_dict_A)
    grid_B = GridSpec(1, len(regions), **pos_dict_B)
    grid_C = GridSpec(1, len(regions), **pos_dict_C)

    ylim = .28
    wpoints = ['W1', 'W2', '31', '32']

    tickl = [labels[w] for w in wpoints]

    box_xs = np.arange(len(wpoints), dtype=float)
    fig = mpl.figure(figsize=(FIG_WIDTH_FULL, 6.4), dpi=200, facecolor='w')


    datadict = dict()

    for ireg, reg in enumerate(regions):
        idx_reg = df.Region == reg
        df_reg = df.loc[idx_reg]
        peak_data_signif = dict()

        asym_data = []
        n_signif = []
        for wpoint in wpoints:
            # print number of ccgs and significant ccgs
            idx_w = (df_reg.timepoint == wpoint) & (df_reg.y_peak > 0)
            n = idx_w.sum()
            idx_signif = idx_w & df_reg.significant
            k = idx_signif.sum()
            n_signif.append(k)
            print(f'In region {reg} and time-point {wpoint}, have {n} CCGs (of these, {k} significant)')
            wpoint_data = df_reg.loc[idx_w, 'asymmetry'].abs()
            asym_data.append(wpoint_data)
            datadict[wpoint] = wpoint_data
            peak_data_signif[wpoint] = df_reg.loc[idx_w, ['x_peak', 'significant', 'ident_pairs']]


        # plot asymmetries
        plot = fig.add_subplot(grid_A[ireg])

        prepare_plot(plot)
        title_pos_y = 1.7
        plot.text(.5, title_pos_y, LONGNAMES[reg],
                size=FONT_SIZE_REGIONS,
                va='bottom', ha='center',
                transform=plot.transAxes,
                weight='bold')

        boxes = plot.boxplot(asym_data, notch=True,
                    patch_artist=True,
                    flierprops=flierprops, positions=box_xs,
                    widths=len(wpoints)*.1)
        transform = blended_transform_factory(plot.transData,
                plot.transAxes)

        for box_x, box, box_content, n_loc in zip(box_xs,
                boxes['boxes'], asym_data, n_signif):

            text = f'{box_content.shape[0]}\n{n_loc}\n{box_content.mean():.4f}'

            plot.text(box_x, 1.05, text,
                    # color=STAGE_COLORS[stage],
                    ha='center',
                    transform=transform)

        # do statistical comparison between SWS first half and SWS second half
        pair1 = ('31', '32')
        pair2 = ('W1', 'W2')
        for pair in (pair1, pair2):
            n1, n2 = pair
            p1 = wpoints.index(n1)
            p2 = wpoints.index(n2)
            statres = scipy.stats.mannwhitneyu(asym_data[p1], asym_data[p2], alternative='two-sided')
            print(f'Asymmetry between {n1} and {n2} in Region {reg}, P = {statres.pvalue:.3g}')
            label_diff(plot, transform, box_xs[p1], box_xs[p2], .8,
                    pstars(statres.pvalue, panel='a', region=LONGNAMES[reg],
                           comparison=f'{labels[n1]} vs {labels[n2]}',
                           test='mannwhitneyu', alternative='two-sided',
                           n1=asym_data[p1].shape[0],
                           n2=asym_data[p2].shape[0],
                           statistic=statres.statistic))


        plot.set_ylim((0, ylim))
        plot.set_xticklabels(tickl, rotation=45)

        if ireg == 0:
            plot.text(-.2, .5, modenames['asymmetry'],
                    transform=plot.transAxes,
                    va='center', ha='center',
                    rotation=90)

            plot.text(0, 1.05, 'N =\nN signif. =\nMean =',
                            ha='right',
                            color='k',
                            transform=plot.transAxes)


        # plot decoding

        plot = fig.add_subplot(grid_B[ireg])
        prepare_plot(plot)
        tpoints = ('W1', 'W2', '31', '32')
        # labels = {'W1': 'Post-exp. first hour',
                #   'W2': 'Post-exp. second hour',
                #   '31': 'SWS first half',
                #   '32': 'SWS second half'}
        plot_asym_shift = fig.add_subplot(grid_C[ireg])
        prepare_plot(plot_asym_shift)
        with pvalue_log.context(region=LONGNAMES[reg]):
            plot_decoding_panel_mod(df_reg.copy(), tpoints, plot, plot_asym_shift)
        if ireg == 0:
            plot_asym_shift.text(-.3, .5, 'Asymmetry of pairs',
                    transform=plot_asym_shift.transAxes, ha='center', va='center',
                    rotation=90)

            plot_asym_shift.set_xticklabels(['SWS (first half)', 'SWS (second half)'])
        else:
            plot_asym_shift.set_xticklabels([])

        plot.set_xticks([])
        plot.set_yticks((0, 50))
        plot.set_xlim((-.5, 3.5))

        if ireg == 0:
            label = r'Fwd | Rev'
            plot.text(-.2, .5, label, transform=plot.transAxes,
                ha='right', va='center', rotation=90)

            legend_pos_y = -.4
            for tp in tpoints:
                plot.bar(-10, 1,
                        color=STAGE_COLORS_PALE_2[tp[0]],
                        hatch=hatches[tp[1]],
                        lw=1,
                        label=labels[tp]) #STAGE_LONGNAMES[tp[0]])
            plot.legend(loc='lower left',
                bbox_to_anchor=(-.1, legend_pos_y),
                ncol=2)

    for i_row, pdict in enumerate((pos_dict_A, pos_dict_B, pos_dict_C)):
        if i_row == 0:
            top = pdict['top'] + .117
        else:
            top = pdict['top'] + .059
        fig.text(pdict['left'] - .07, top, 'acb'[i_row],
               size=FONT_SIZE_LETTERS, weight='bold')


    pvalue_log.write('fig_S_11')
    save_figure(fig, 'fig_S_11', dpi=200)

if __name__ == "__main__":
    set_paper_style()
    df = get_data()
    print(df.utype.unique())
    with pvalue_log.context(figure='fig_S_11'):
        plot_extra_information_phases(df)
