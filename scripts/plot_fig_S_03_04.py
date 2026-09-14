"""
Example neurons, one figure per unit.

Each figure is the screening and recall raster block of Fig02 for a single
unit; for two of the units the full-night timeline is shown next to it.
"""
import matplotlib.pyplot as mpl
from matplotlib.gridspec import GridSpec

from figure_tools.definitions import (FONT_SIZE_LETTERS, FIG_WIDTH_FULL,
        FIG_WIDTH_HALF)

from figure_tools.session_information import read_session_info

from figure_tools.plot_timeline import plot_sleep_timeline

from figure_tools.plot_screening import plot_screening, make_raster_plots

from figure_tools.unit_data import load_unit

from figure_tools.screening_data import load_screening

from figure_tools.style import set_paper_style, save_figure

MORNING_SCREENING = {
    (716, 1, 12, 'pos', 1): '716ps1_CSC12',
    (716, 1, 66, 'pos', 1): '716ps1_CSC66',
    (717, 2, 30, 'pos', 1): '717ps3_CSC30',
    (717, 2, 66, 'pos', 1): '717ps3_CSC66',
    (717, 2, 68, 'pos', 1): '717ps3_CSC68',
}

SAMPLES = (
    (707, 2, 48, 'pos', 6, 6, True, 'c', 'fig_S_03_a'),
    (710, 1, 15, 'pos', 2, 4, True, 'a', 'fig_S_03_b'),
    (716, 1, 66, 'pos', 1, 8, False, None, 'fig_S_04_a'),
    (717, 2, 30, 'pos', 1, 7, False, None, 'fig_S_04_b'),
    (717, 2, 66, 'pos', 1, 5, False, None, 'fig_S_04_c'),
)


def plot_example(info, unit, stim, add_times, add_times_e, do_night,
                 start_letter):
    """
    draw one example unit, optionally next to its full-night timeline
    """
    if do_night:
        fig = mpl.figure(figsize=(FIG_WIDTH_FULL, 4.37))
        row_grid = GridSpec(1, 2, left=.06, right=.97, bottom=.084,
            top=.965, wspace=.4, hspace=.5)

        bottom, top, left, right = row_grid.get_grid_positions(fig)
        use_width = right[1] - left[0]

        width_tcourse = use_width*.5
        width_screening = use_width*.4
        left_screening = right[1] - width_screening

        shift = .2
        h_tcourse = (top[0] - bottom[0])/2 - shift
        pos_tcourse_lower = [left[0], bottom[0]+shift,
                width_tcourse, h_tcourse]

        pos_tcourse_upper = list(pos_tcourse_lower)
        pos_tcourse_upper[1] += h_tcourse

    else:
        fig = mpl.figure(figsize=(FIG_WIDTH_HALF, 5))
        left_screening = .15
        width_screening = .8
        top = [.92]
        bottom = [.15]

    pos_scr = [left_screening, bottom[0], width_screening, top[0] - bottom[0]]

    param = dict()
    param['stimname_size'] = 9
    param['recall_pre_ms'] = 10 * 1000
    param['recall_post_ms'] = 10 * 1000
    param['recall_upper_ytick'] = 10

    # the morning row exists exactly when there is morning data to put in it
    do_morning = add_times is not None
    plots = make_raster_plots(fig, pos_scr, do_morning)
    plot_screening(plots, info.stimulus_frame, unit, stim, param,
                   add_times, add_times_e)

    if do_night:
        param['amp_ylabel_dist'] = -.07
        param['amp_ylim'] = (0, 149)
        param['stage_ylim'] = (-4, 4.5)
        param['vline_ymax'] = 1.6

        plot_sleep_timeline(fig, pos_tcourse_upper, pos_tcourse_lower,
                info, unit, param)

        letter_pos = [[left[0] - .05, top[0]], [left[1] - .03, top[0]]]
        if start_letter is not None:
            for ipos, pos in enumerate(letter_pos):
                letter = chr(ord(start_letter) + ipos)
                fig.text(pos[0], pos[1], letter,
                        size=FONT_SIZE_LETTERS, weight='bold')

    return fig


def do_plot(pat, ses, channel, sign, cluster, stim, do_night, start_letter,
            name):
    """
    draw and save the figure for one example unit
    """
    info = read_session_info(pat, ses)
    unit = load_unit('{}_CSC{}_{}_{:02d}'.format(info.infix, channel, sign,
                                                 cluster))

    add_times = add_times_e = None
    screening_name = MORNING_SCREENING.get((pat, ses, channel, sign, cluster))
    if screening_name is not None:
        print('Loading morning screening data')
        add_times, add_times_e = load_screening(screening_name)

    fig = plot_example(info, unit, stim, add_times, add_times_e, do_night,
                       start_letter)

    save_figure(fig, name, dpi=300, pdf_dpi=300)
    mpl.close(fig)


if __name__ == '__main__':
    set_paper_style()
    for sample in SAMPLES:
        do_plot(*sample)
