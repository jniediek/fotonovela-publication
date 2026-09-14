"""
Fig S07: hippocampal ripple central frequency in wakefulness and SWS.

One boxplot per sleep stage, over the same channel-wise ripple table that
Fig05 panel B draws the ripple rates from.
"""
import matplotlib.pyplot as mpl
from matplotlib.gridspec import GridSpec

from figure_tools.plot_ripple_stats import plot_ripple_frequencies
from figure_tools import pvalue_log
from figure_tools.ripple_data import load_swr_rates
from figure_tools.style import set_paper_style, save_figure


def main():

    fig = mpl.figure(figsize=(2.5, 3), dpi=120, facecolor='w')
    grid = GridSpec(1, 1, left=.3, right=.8, top=.8, bottom=.2)
    df = load_swr_rates()

    freq = 'highend'
    idx = (df.Freq == freq) #& (df.N_ripples > 20)

    plot = fig.add_subplot(grid[0, 0])
    with pvalue_log.context(figure='fig_S_07'):
        plot_ripple_frequencies(plot, df[idx])
    plot.set_ylabel('Ripple central frequency\n[Hz]')

    pvalue_log.write('fig_S_07')
    save_figure(fig, 'fig_S_07', dpi=250)


if __name__ == '__main__':
    set_paper_style()
    main()
