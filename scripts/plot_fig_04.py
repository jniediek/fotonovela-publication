import matplotlib.pyplot as mpl
from matplotlib.gridspec import GridSpec

from figure_tools.definitions import (FIG_WIDTH_FULL,
                                      FONT_SIZE_LETTERS)
from figure_tools.plot_cohen import draw_cohen_bars, draw_stats
from figure_tools.population import load_population
from figure_tools import pvalue_log
from figure_tools.session_information import read_session_info
from figure_tools.sleep_data import load_sleep_frates
from figure_tools.style import set_paper_style, save_figure


def load_data():
    return load_sleep_frates()


def plot_stats(info, trow, df, reg_idxs, invariant_idxs):

    row_grid = GridSpec(1, 3, left=.06, right=.9, bottom=.12,
            top=.82, wspace=.4, hspace=.5, width_ratios=[3, 3, 2])

    fig = mpl.figure(figsize=(FIG_WIDTH_FULL, 3))

    pos_bars = fig.add_subplot(row_grid[0, 1])
    plots_perc = [fig.add_subplot(row_grid[0, 2])]
    plots_dots = [fig.add_subplot(row_grid[0, 0])]

    draw_cohen_bars(fig, pos_bars, info, trow.Channel,
            trow.Sign, trow.Cluster, df)

    param = {
        'label_long': True,
        'do_heading': False,
        'stats_do_xtext': True,
        'stats_compare_dist': -.12,
        'stage_angle': None,
        'perc_xlim': (-.5, 1.5),
        'small_arrow_size': 16,
        'invariant_name': 'inv',
        'do_titles': True,
        'ypos_N': 1.06,
        'panel_dots': 'a',
        'panel_perc': 'c'
    }

    with pvalue_log.context(figure='fig_04'):
        draw_stats(plots_dots, plots_perc,
                df, reg_idxs, ['H'], invariant_idxs['inv'], param)

    lshift = .12

    bottom, top, left, right = row_grid.get_grid_positions(fig)

    letter_pos = [[left[0] - .05, top[0] + lshift],
            [left[1] - .08, top[0] + lshift],
            [left[2] - .08, top[0] + lshift]]

    for pos, letter in zip(letter_pos, 'abc'):
        fig.text(pos[0], pos[1], letter,
                size=FONT_SIZE_LETTERS, weight='bold')

    return fig


def main(irow):
    def ident_gen(row):
        return f"{row.Patient:03d}_{row.Session:02d}_{row.Channel:03d}_sort_{row.Sign}_joh_{row.Cluster:02d}"

    df = load_data()

    df.ident = df.apply(ident_gen, axis=1)

    pop = load_population()

    df = df.merge(pop[['ident', 'is_selective', 'is_inv',
                       'is_no_resp', 'is_consistent', 'Simple_Region']], on='ident')

    reg_idxs = dict()
    invariant_idxs = dict()
    for reg in ('A', 'H', 'PHC'):
        reg_idxs[reg] = df.Simple_Region == reg

    invariant_idxs['inv'] = df.is_inv & df.is_consistent

    # idx = reg_idxs['H'] & invariant_idxs['inv']
    idx_trow = ((df.Patient == 710) &
                (df.Session == 1) &
                (df.Channel == 15) &
                (df.Sign == 'pos') &
                (df.Cluster == 2))
    trow = df[idx_trow]
    assert(trow.shape[0] == 1)
    trow = trow.iloc[0]

    pat, ses = (trow.Patient, trow.Session)
    print(pat, ses)
    info = read_session_info(pat, ses)
    fig = plot_stats(info, trow, df, reg_idxs, invariant_idxs)
    pvalue_log.write('fig_04')
    save_figure(fig, 'fig_04', dpi=300)
    mpl.close(fig)


if __name__ == '__main__':
    set_paper_style()
    main(11)
