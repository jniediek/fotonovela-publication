import matplotlib.pyplot as mpl
from matplotlib.gridspec import GridSpec

from figure_tools.definitions import FIG_WIDTH_FULL

from figure_tools.session_information import channel_names

from figure_tools.plot_ripple import plot_swr_event

from figure_tools.swr_data import load_swr_event

from figure_tools.style import set_paper_style, save_figure

HEMISPHERES = {'L': 'Left', 'R': 'Right'}

EXAMPLES = ((712, 1, 30, '712fn1_CSC30_swr_227423339', 'SWS'),
            (712, 2, 57, '712fn2_CSC57_swr_289125783', 'SWS'),
            (717, 1, 70, '717fn1_CSC70_swr_314576834', 'Awake'))

WIDTH_RATIOS = [76, 4, 20]


def plot_example(plots, pat, ses, channel, name, stage, do_texts,
                 do_texts_right):
    """
    draw one example column and title it with its hemisphere and centre
    frequency
    """
    swr_event = load_swr_event(name)
    centre_freq = plot_swr_event(plots, swr_event, do_texts, do_texts_right)

    hemisphere = HEMISPHERES[channel_names(pat, ses)[channel][0]]
    plots[0].set_title(f'{hemisphere} Hippocampus\n{stage}\n'
                       f'Cent. freq. {centre_freq:.1f} Hz')


def main():
    fig = mpl.figure(figsize=(FIG_WIDTH_FULL, 5), dpi=120)
    outer_grid = GridSpec(1, 3, left=.1, right=.9, top=.9)

    for i_ex, example in enumerate(EXAMPLES):
        inner_grid = outer_grid[i_ex].subgridspec(
            3, 3, width_ratios=WIDTH_RATIOS)
        plots = [fig.add_subplot(inner_grid[i]) for i in [0, 3, 6, 7]]

        plot_example(plots, *example, do_texts=i_ex < 1,
                     do_texts_right=i_ex == len(EXAMPLES) - 1)

        if i_ex > 0:
            for plot in plots:
                plot.set_ylabel('')

    save_figure(fig, 'fig_S_08', dpi=250)


if __name__ == '__main__':
    set_paper_style()
    main()
