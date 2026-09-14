import numpy as np
import scipy.stats
import matplotlib.pyplot as mpl
from matplotlib.gridspec import GridSpec

from figure_tools.definitions import (FIG_WIDTH_FULL,
                                      FONT_SIZE_LETTERS, LONGNAMES)
from figure_tools.emerging_data import load_and_merge_correlations
from figure_tools.plot_stats import label_diff, pstars
from figure_tools import pvalue_log
from figure_tools.style import set_paper_style, save_figure

letter_x = -.35
letter_y = 1.02


def create_supp_plot(df):

    cols = ('e_pre', 'e_fn_l', 'W1', 'W2', '3')
    names = {'e_pre': 'Pre-experiment', 'e_fn_l': 'Learning',
             'e_fn_r': 'Recall',
             'W1': 'W (hour 1)', 'W2': 'W (hour 2)', '3': 'SWS'}

    df = df[df.Channel_1 != df.Channel_2]
    df = df[df['preferred_stim_num_1'] != df['preferred_stim_num_2']]

    fig = mpl.figure(figsize=(FIG_WIDTH_FULL, 5), facecolor='w', dpi=200)

    grid = GridSpec(2, 3, left=.1, right=.95, bottom=.1, top=.93, hspace=.8, wspace=.5)
    reg = 'H'
    idx = (df.Simple_Region_1 == reg) & (df.Simple_Region_2 == reg)
    df_loc = df[idx].copy()

    boxdata = []
    xdata = []
    letters = ('bcdef')
    for icol, col in enumerate(cols):

        ax = fig.add_subplot(grid[icol + 1])
        ax.text(letter_x, letter_y, letters[icol], transform=ax.transAxes, size=FONT_SIZE_LETTERS, weight='bold')
        c2 = 'Corr_' + col
        c1 = 'Corr_e_fn_r'
        ax.scatter(df_loc[c1], df_loc[c2], s=.8, c='C0')
        if col == 'e_pre':
            local_idx = df_loc.Duration_pre > 30 * 1000
            d = df_loc.loc[local_idx, [c1, c2]].dropna().to_numpy()
        else:
            d = df_loc[[c1, c2]].dropna().to_numpy()
        if d.shape[0] < 2:
            rho = np.nan
            pval = np.nan
        else:
            [rho, pval] = scipy.stats.pearsonr(d[:, 0], d[:, 1])

        ax.xaxis.grid(True)
        ax.yaxis.grid(True)
        for p in ('top', 'right'):
            ax.spines[p].set_visible(False)
        ax.set_axisbelow(True)
        ax.plot([-1, 1], [-1, 1], lw=.5, ls='--')
        ax.set_xlim((-.3, .4))
        ax.set_ylim((-.3, .4))

        ax.set_xlabel('$r_{SC}$ Recall')
        ax.set_ylabel('$r_{SC}$ ' + names[col], size=7)
        ax.text(0, 1.01, f'{d.shape[0]} pairs (rho = {rho:.3g} '
                 f'{pstars(pval, panel=letters[icol], region=LONGNAMES[reg],
                           comparison=f"{names['e_fn_r']} vs {names[col]}",
                           test='pearsonr', alternative='two-sided',
                           n1=d.shape[0], statistic=rho)})',
                 transform=ax.transAxes, va='bottom', size=6)
        print(f'{names[col]}: rho = {rho:.3f}, p = {pval:.3g}' )

    cols = ('e_pre', 'e_fn_l', 'e_fn_r',  'W1', 'W2', '3' )
    boxdata = []
    xdata = []
    labels = []

    val = df_loc.Corr_e_fn_r
    df_loc['diff'] = val
    ingroup = df_loc['diff'] > val.median()
    ax = fig.add_subplot(grid[0])
    ax.yaxis.grid(True)
    for p in ('top', 'right'):
        ax.spines[p].set_visible(False)
    ax.set_title(reg)

    for icol, col in enumerate(cols):
        if col == 'e_pre':
            local_idx = df_loc.Duration_pre > 30 * 1000
            coldata1 = df_loc.loc[local_idx & ingroup, 'Corr_' + col].dropna().to_numpy()
            coldata2 = df_loc.loc[local_idx & ~ingroup, 'Corr_' + col].dropna().to_numpy()
        else:
            coldata1 = df_loc.loc[ingroup, 'Corr_' + col].dropna().to_numpy()
            coldata2 = df_loc.loc[~ingroup, 'Corr_' + col].dropna().to_numpy()

        if coldata1.any():
            [T, p] = scipy.stats.mannwhitneyu(coldata1, coldata2)
        else:
            continue
        boxdata += [coldata1, coldata2]
        xdata += [3*icol, 3*icol + 1]
        labels += ['high', 'low']

        print(reg, col, f'N1 = {coldata1.shape[0]} N2 = {coldata2.shape[0]} mhigh = {coldata1.mean():.4g} mlow = {coldata2.mean():.4g} p = {p:.4g}')
        label_diff(ax, ax.transData, 3*icol, 3*icol+1, .42,
                pstars(p, panel='a', region=LONGNAMES[reg],
                       comparison=f'{names[col]}, high vs low recall',
                       test='mannwhitneyu', alternative='two-sided',
                       n1=coldata1.shape[0], n2=coldata2.shape[0],
                       statistic=T))
        ax.text(3*icol, .5, coldata1.shape[0], rotation=0, size=5, ha='center')
        ax.text(3*icol + 1, .5, coldata2.shape[0], rotation=0, size=5, ha='center')

        ax.text(3*icol + .5, -.62, names[col], size=7, ha='center', rotation=90, va='center')

    ax.boxplot(boxdata, positions=xdata, flierprops={'marker': 'x', 'markersize': 1, 'markeredgecolor': None})
    ax.set_xticklabels(labels, rotation=90, size=7)

    ax.set_ylim((-.25, .6))
    ax.set_title('Median split on recall')
    ax.text(letter_x, letter_y, 'a', transform=ax.transAxes, size=FONT_SIZE_LETTERS, weight='bold')
    ax.set_ylabel('$r_{SC}$')

    pvalue_log.write('fig_S_10')
    save_figure(fig, 'fig_S_10')


if __name__ == "__main__":
    set_paper_style()
    df = load_and_merge_correlations()
    with pvalue_log.context(figure='fig_S_10'):
        create_supp_plot(df)
