import numpy as np
import seaborn as sns
import matplotlib.pyplot as mpl
import pandas as pd


from figure_tools.style import set_paper_style, save_figure
from figure_tools.definitions import (FONT_SIZE_LETTERS, FIG_WIDTH_FULL,
        FOLDER_PERFORMANCE)
from figure_tools.session_information import read_session_info
from figure_tools.plot_timeline import plot_sleep_timeline
from figure_tools.plot_screening import plot_screening, make_raster_plots
from figure_tools.tools_fig_02 import COLOR_LINES
from figure_tools.unit_data import load_unit
from figure_tools.screening_data import load_screening

VGAP = .05
HGAP = .05
LGAP = .1

BOTTOM_C = .77
HEIGHT_B = (1/4 - VGAP)*.6
HEIGHT_C = (1/4 - VGAP)*.4
WIDTH_BC = (1 - LGAP)*.6 - HGAP - .03
WIDTH_F = (1 - LGAP)*.4 - 2*HGAP
POS_timeline_1 = (LGAP + WIDTH_F + .12 , BOTTOM_C + HEIGHT_C + .02, WIDTH_BC, HEIGHT_B)
POS_timeline_2 = (LGAP + WIDTH_F + .12 , BOTTOM_C, WIDTH_BC, HEIGHT_C)

BOTTOM = .05
HEIGHT_DE = .68 - 2*VGAP
WIDTH_DE = 0.355

POS_D = (LGAP, BOTTOM, WIDTH_DE, HEIGHT_DE)
POS_E = (LGAP + WIDTH_DE + 2*HGAP + .03, BOTTOM, WIDTH_DE, HEIGHT_DE)
LEFT_F = LGAP + WIDTH_BC + HGAP + 1.5*HGAP + .03
POS_performance = (LGAP, BOTTOM_C, WIDTH_F, HEIGHT_B + HEIGHT_C - .5*VGAP)

def plot_D(fig, frame):

    plot = fig.add_axes(POS_performance)
    for pos in ('top', 'right'):
        plot.spines[pos].set_visible(False)

    # the rows of data are the first and sixth evening testing, and the morning testing
    data = frame.loc[:, ['E1', 'E6', 'M']]

    mean = 100*np.nanmean(data, 0)
    sns.swarmplot(100*data, size=1.2,
                  color=COLOR_LINES, alpha=.8)
        
    plot.set_xticklabels([])
    labels = ((.5, 0, 'Evening: 6 repeats'),
              (-.5, 1, 'Repeat'),
              (0, 1, '#1'),
              (1, 1, '#6'),
              (2, 0, 'Morning: 1 repeat'),
              (2, 1, '#1'))

    for x, y, label in labels:
        plot.text(x, 6*y + 35, label,
                  va='top', ha='center')

    for i, col in enumerate(('E1', 'E6', 'M')):
        plot.text(i, 107, data[col].count(),
                  ha='left', va='top')

        # indicate the mean
        plot.plot([i-.1, i+.1], [mean[i], mean[i]],
                lw=1.5, zorder=4, alpha=.7, color='k')
        print(f"{col}: {(data[col] > .999).sum()} perfect (out of {data[col].count()})")
    plot.set_ylim((45, 100))
    
    plot.set_ylabel('Items recalled correctly [%]')
    plot.text(-.1, 107, 'N sessions =', ha='right',
              va='top')


def do_plot(taskstr):

    fig = mpl.figure(figsize=(FIG_WIDTH_FULL, 7))
    plots = {}
    
    param = dict()

    if ('B' in taskstr) or ('C' in taskstr):
        info_2 = read_session_info(716, 1)
        info_1 = read_session_info(717, 2)

        unit_2 = load_unit('716fn1_CSC12_pos_01')
        unit_1 = load_unit('717fn2_CSC68_pos_01')

        stim_2 = 1
        stim_1 = 3

        add_times_2, add_times_2e = load_screening('716ps1_CSC12')
        add_times_1, add_times_1e = load_screening('717ps3_CSC68')

    # this plots the full night recording 
    if 'B' in taskstr:
        param['amp_ylabel_dist'] = -.06
        param['amp_ylim'] = (0, 90)
        param['stage_ylim'] = (-1.5, 6.5)
        param['vline_ymax'] = 1.9
        plots['B1'], plots['B2'] = plot_sleep_timeline(fig, POS_timeline_1, POS_timeline_2,
                info_1, unit_1, param)
   
    if 'C' in taskstr:
        param['stimname_size'] = 11
        param['recall_pre_ms'] = 10 * 1000
        param['recall_post_ms'] = 10 * 1000
        sets = ((POS_E, info_1.stimulus_frame, unit_1, stim_1, 10, add_times_1, add_times_1e),
                (POS_D, info_2.stimulus_frame, unit_2, stim_2, 20, add_times_2, add_times_2e))

        for pos, stimulus_frame, unit, stim, yt, add_times, add_times_e in sets:
            param['recall_upper_ytick'] = yt

            plots = make_raster_plots(fig, pos, has_morning=True)
            plot_screening(plots, stimulus_frame, unit, stim, param, add_times, add_times_e)

    if 'D' in taskstr:
        performance_frame = pd.read_csv(FOLDER_PERFORMANCE /
                                        'performance_frame.csv')
        plot_D(fig, performance_frame)
   
    corr = .03
    letterdata = {
                  'a': (.001, BOTTOM_C + HEIGHT_C + HEIGHT_B + .01),
                  'c': (.001, BOTTOM + HEIGHT_DE + corr),
                  'b': (WIDTH_F + .15, BOTTOM_C + HEIGHT_C + HEIGHT_B + .01)}

    titles = {'b': 'Full-night recording',
    'a': 'Recall performance',
    'c': 'Neuronal responses during screening and recall'}

    for letter, pos in letterdata.items():
        x, y = pos
        fig.text(x, y, letter.lower(), size=FONT_SIZE_LETTERS, weight='bold')
        fig.text(x + .03, y, titles[letter], weight='bold')

    save_figure(fig, 'fig_02', dpi=300, pdf_dpi=300)
    

if __name__ == '__main__':
    set_paper_style()
    do_plot('CDB')
