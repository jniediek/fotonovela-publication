import numpy as np
import scipy.signal as signal

T_PRE_MS = 15 * 1000
T_POST_MS = 15 * 1000
COLOR_LINES = (0, 0, .5)

def plot_recall(plot, plot_hist, times, onset_times, params):

    t_pre = params['recall_pre_ms']
    t_post = params['recall_post_ms']
    lw = .7 
    smooth_lw = .7
    std = 300

    for tplot in (plot, plot_hist):
        tplot.axvline(0, color='k', lw=.5, ymax=1.05, clip_on=False)
        xticks = np.arange(-T_PRE_MS, T_POST_MS + 5000, 5000)
        tplot.set_xticks(xticks)
        tplot.set_xticklabels((xticks/1000).astype(int))
        tplot.set_xlabel('Time around recall [sec]')

        for where in ('left', 'right', 'top', 'bottom'):
            tplot.spines[where].set_visible(False)
 

    fr_bins = np.arange(-t_pre-500, t_post+500, 1)
    nsamp_window = 10 * std
    fr_window = signal.get_window(('gaussian', std), nsamp_window)
    fr_window = 1000/fr_window.sum() * fr_window
    fr_w = int(round(nsamp_window/2 - 1))
    evlist = []
    colors = []
    response_list = []

    for tcenter in onset_times:
        idx = (times >= tcenter - T_PRE_MS) &\
            (times <= tcenter + T_POST_MS)

        if idx.any():
            appender = times[idx] - tcenter
            hist, _ = np.histogram(appender, fr_bins)
            # we now do the smoothing of each trial individually, to get a STD
            smooth = signal.convolve(hist, fr_window)[fr_w:-fr_w]
            response_list.append(smooth)
             
        else:
            # old trick for empty arrays 
            appender = [-2 * T_PRE_MS]

        evlist.append(appender)
        colors.append('k')


    matrix = np.vstack(response_list)
    mean = matrix.mean(0)
    sem = matrix.std(0)/np.sqrt(matrix.shape[0])
    plot_hist.plot(fr_bins, mean, color=COLOR_LINES, lw=smooth_lw)
    plot_hist.fill_between(fr_bins, mean-sem, mean+sem, alpha=.1, color=COLOR_LINES)

    plot.eventplot(evlist[::-1], colors=COLOR_LINES, lw=lw)

    for tplot in (plot, plot_hist):
        tplot.set_xlim((-t_pre, t_post))
    plot.set_ylim((-.5, len(evlist) - .5))
    plot.set_xticks([])
    plot.set_yticks([])
    plot_hist.set_yticks([0, params['recall_upper_ytick']])
    plot_hist.set_yticklabels([0, '{} Hz'.format(params['recall_upper_ytick'])])
    
    for pos in (len(evlist)-.2, -.8):
        plot.axhline(pos, xmin=-.03, color='grey', lw=.5, clip_on=False)
    plot_hist.axhline(0, xmin=-.03, color='grey', lw=.5, clip_on=False)
