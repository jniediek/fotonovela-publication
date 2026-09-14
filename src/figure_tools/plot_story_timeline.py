import numpy as np
import matplotlib.pyplot as mpl
import matplotlib.cm as cm
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle

from figure_tools.definitions import FOLDER_STIM_PICTURES

COLOR_SPIKES = '#333377'

MEW_SPIKE = 1 / 12
MEW_STIM = 4 / 12
MS_TICK = 10 / 12
LW_FRAME = 10 / 12


def plot_story_timeline(fig, stimuli, spike_times, target_index):
    """
    plots all information available for this cluster and this story
    """
    colors = cm.nipy_spectral(np.linspace(0, 1, len(stimuli)))
    nstim = len(stimuli)

    grid = GridSpec(2, nstim, left=.02, bottom=.15, right=.98, top=.98)

    scale = fig.get_size_inches()[0]

    target_times = stimuli[target_index]['times']

    start = 45 * 1000
    stop = 50 * 1000

    # do the colorful boxes
    for i, stim in enumerate(stimuli):
        p_im = fig.add_subplot(grid[0, i])
        p_im.set_xticks([])
        p_im.set_yticks([])
        p_im.set_xlim((0, 170))
        p_im.set_ylim((170, 0))
        mpl.setp(p_im.spines.values(), visible=False)
        p_im.add_artist(Rectangle((5, 5), 160, 160,
                        color=colors[i], fill=False, lw=LW_FRAME*scale))
        p_im.imshow(mpl.imread(FOLDER_STIM_PICTURES / stim['filename']))

        # the pictures are placeholders and all look alike, so name them
        p_im.text(85, -5, stim['stim_name'].replace(' ', '\n'),
                  ha='center', va='bottom')

        if i == target_index:
            p_target = p_im

    p_spikes = fig.add_subplot(grid[1, :])
    for key in ('left', 'right'):
        p_spikes.spines[key].set_visible(False)

    p_spikes.set_ylim((len(target_times), -1))
    p_spikes.set_xlim((-start/1000, stop/1000))
    p_spikes.set_xlabel('sec')
    p_spikes.set_yticks([])

    for i, t in enumerate(target_times):
        index = (spike_times >= t - start) & (spike_times <= t + stop)
        plot_times = spike_times[index] - t
        lt = len(plot_times)
        p_spikes.plot(plot_times/1000, i * np.ones(lt), '|',
                      color=COLOR_SPIKES,
                      mew=MEW_SPIKE*scale, ms=MS_TICK*scale)

    for i, stim in enumerate(stimuli):
        times = stim['times']
        for j, t in enumerate(times):
            plot_times = t - target_times[j]
            p_spikes.plot(plot_times/1000, j, '|',
                          color=colors[i],
                          mew=MEW_STIM*scale, ms=MS_TICK*scale)

    # the raster is aligned to the target stimulus, which sits at time 0
    p_spikes.annotate('', xy=(0, -1), xytext=(85, 170),
                      textcoords=p_target.transData,
                      arrowprops={'arrowstyle': '->',
                                  'color': colors[target_index]})
