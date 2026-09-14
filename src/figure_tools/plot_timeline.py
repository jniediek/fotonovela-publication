import numpy as np
from matplotlib.dates import date2num, DateFormatter, HourLocator
from matplotlib.patches import Rectangle

from figure_tools.tools_fig_02 import (nlx_to_mpl, STAGEDICT, COLOR_LINES,
        COLOR_LEARN, COLOR_SCR_E, COLOR_SCR_M, COLOR_RECALL)
from figure_tools.make_border_dict import make_border_dict

def plot_sleep_timeline(fig, pos1, pos2, info, unit, param):
    """
    Plot a timeline of sleep
    """
    # required fields of info: 
    # - start_datetime
    # - sleepstages
    # - stimulus_frame
    # - start_nlx
    # - stop_nlx
    mpl_start = date2num(info.start_datetime)
    sleepstages = info.sleepstages

    locator = HourLocator(interval=1)
    
    # two axes, because y units differ, but one common x axis with real time
    plots = []
    for pos in (pos1, pos2):
        plot = fig.add_axes(pos)
        for spine in plot.spines.values():
                spine.set_visible(False)
        plots.append(plot)
        plot.xaxis.set_major_locator(locator)
        
    plots[1].spines['bottom'].set_visible(True)
    
    last_bit = np.array((sleepstages['stoptime'][-1],
                         info.stop_nlx + 300 * 1000, 'W'),
                         dtype=sleepstages.dtype)
        
    all_stages = np.append(sleepstages, last_bit)

    # top plot is the hypnogram + experimental phases
    plot_starts = nlx_to_mpl(all_stages['starttime'],
                             info.start_nlx, mpl_start)
    plot_stops = nlx_to_mpl(all_stages['stoptime'],
                            info.start_nlx, mpl_start)

    xaxis_stop = plot_stops[-1]
    
    timeaxis = np.vstack((plot_starts, plot_stops)).T.ravel()
    stageaxis = np.zeros((all_stages.shape[0], 2), int)
    
    for key in STAGEDICT:
        stageaxis[all_stages['stage'] == key, :] = (STAGEDICT[key], STAGEDICT[key])

    stageaxis = stageaxis.ravel()
    
    plot = plots[0]
    plot.plot(timeaxis, stageaxis, color=COLOR_LINES, lw=.7)
    plot.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    plot.set_xlim((plot_starts[0], xaxis_stop))

    # do the REM in bold
    for i, row in enumerate(all_stages['stage']):
        if row == 'R':
            rect = Rectangle((plot_starts[i], STAGEDICT['R']),
                             plot_stops[i] - plot_starts[i], .3,
                             fc=COLOR_LINES, edgecolor='none')
            plot.add_artist(rect)

    # this ylim controls how much the gap between A and B is filled with text
    plot.set_ylim(param['stage_ylim'])
    plot.set_yticks((-3, -2, -1, 0, 1))
    plot.set_yticklabels(('3', '2', '1', 'R', 'W'))
    plot.set_xticklabels([])
    
    # include the experimental phases (MS, L, R)
    border_dict = make_border_dict(info.stimulus_frame)
    for name, times in border_dict.items():
        if times is None:
            continue
        else:
            plot_times = nlx_to_mpl(np.array(times),
                             info.start_nlx, mpl_start)
            shift = 0
            edgecolor = 'none'
    
            if 'e_scr_pre' in name:
                color = COLOR_SCR_E
                shift = -10/(24*60)
                label = 'Screening 1'
                yshift = 1.5
            elif 'e_scr_post' in name:
                color = COLOR_SCR_E
                shift = 14/(24*60)
                label = 'Screening 2'
                yshift = 0
            elif 'm_scr_post' in name:
                color = COLOR_SCR_M
                label = 'Screening 3'
                shift = 4/(24*60)
                yshift = 0
            elif 'fn_l' in name:
                color = COLOR_LEARN
                label = 'Learning'
                yshift = 1
                edgecolor = 'w'
                shift = -4/(24*60)
            elif 'fn_r' in name:
                color = COLOR_RECALL
                if 'e' in name:
                    shift = 7/(24 * 60)
                    yshift = .5
                    label = 'Recall 1'
                if 'm' in name:
                    shift = -6/(24 * 60)
                    yshift = .5
                    label = 'Recall 2'
    
            else:
                continue
            rec = Rectangle((plot_times[0], -4),
                    (plot_times[1] - plot_times[0]), 5, ec=edgecolor,
                    lw=.4, facecolor=color, zorder=10)
            plot.add_patch(rec)
            
            plot.text(plot_times[0] + shift, 1.5, label, color=color,
                      va='bottom', ha='left', rotation=45,
                      weight='bold', size=5)
    plot.text(param['amp_ylabel_dist'], .2, 'Sleep stage', va='center', ha='right',
            transform=plot.transAxes, rotation=90)
    plot.xaxis.set_ticks_position('none')

    # now the timeline of one neuron
    
    plot = plots[1]
    plot_times = nlx_to_mpl(unit['times'],
                             info.start_nlx, mpl_start)
    plot_voltages = unit['amplitudes']
    # the pixel marker has no size in a vector file, rasterize this one artist
    # so the amplitude cloud prints as it does in the reference figure
    plot.plot(plot_times, plot_voltages, ls='none', marker=',',
            mec='none', color=COLOR_LINES, rasterized=True)
    plot.set_ylim(param['amp_ylim'])
    plot.set_xlim((plot_starts[0], xaxis_stop))
    plot.text(param['amp_ylabel_dist'], .5, u'µV', ha='right', va='center',
            transform=plot.transAxes, rotation=90)

    plot.xaxis.set_major_formatter(DateFormatter('%H:%M'))

    for tick in plot.get_xticks():
        plot.axvline(tick, color='grey', zorder=0, clip_on=False,
                ymin=0, ymax=param['vline_ymax'], lw=.5)
    for label in plot.get_xticklabels():
        label.set(rotation=45, ha='right', rotation_mode='anchor')

    plot.set_xlabel('Time of day')
    
    return plots

