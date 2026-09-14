import numpy as np
import matplotlib.pyplot as mpl
import matplotlib.cm as cm

from figure_tools.tools_fig_02 import COLOR_LINES

LW_RIPPLE = .3
COLORMAP = cm.jet

XLIM = (-150, 150)
XTICKS = (-100, 0, 100)

RIPPLE_BAND = (59, 250)

CUTOFF_FREQS = (60, 250)

SPIKE_MARKER_Y = 250

YLABELS = ('V [µV]', 'V [µV]', 'f [Hz]')


def centre_frequency(freqs, stockwell_mean):
    """
    frequency of strongest power within the ripple band

    Takes the time-averaged spectrogram of the whole event, which is computed
    when the event is imported (see figure_tools.swr_data).
    """
    low, high = RIPPLE_BAND
    idx = (freqs > low) & (freqs < high)
    return freqs[idx][stockwell_mean[idx].argmax()]


def plot_raw(plot, times, rawdata):
    plot.plot(times, rawdata, color=COLOR_LINES, lw=LW_RIPPLE)
    plot.xaxis.grid(True)
    plot.set_xlim(XLIM)
    plot.set_xticks(XTICKS)
    plot.set_xticklabels([])
    plot.set_ylim((rawdata.min() * 1.2, rawdata.max() * 1.2))


def plot_filtered(plot, times, filt_signal, swr_event, timeshift):
    plot.plot(times, filt_signal, color=COLOR_LINES, lw=LW_RIPPLE)
    plot.xaxis.grid(True)
    plot.set_xlim(XLIM)
    plot.set_xticks(XTICKS)
    plot.set_xticklabels([])
    plot.set_ylim((filt_signal.min() * 1.2, 300))

    for name in swr_event.files:
        if 'unit_times' not in name:
            continue
        spikes = swr_event[name] - timeshift
        if not spikes.shape[0]:
            continue
        marked = int(name.split('_')[-1]) == swr_event['marked_unit']
        color = 'r' if marked else 'b'
        plot.plot(spikes, SPIKE_MARKER_Y + np.zeros(spikes.shape[0]),
                  color + '|', ms=6, mew=1)


def plot_spectrogram(plot, cax, stockwell, freqs):
    vmin = np.percentile(stockwell, 2)
    vmax = np.percentile(stockwell, 98)
    image = plot.imshow(stockwell, aspect='auto',
                        extent=[XLIM[0], XLIM[1], freqs[0], freqs[-1]],
                        origin='lower', cmap=COLORMAP, vmin=vmin, vmax=vmax)
    mpl.colorbar(image, cax=cax)

    plot.set_xlabel('t [ms]')
    plot.set_xticks(XTICKS)

    for cutoff_freq in CUTOFF_FREQS:
        plot.axhline(cutoff_freq, color='w', lw=.8, ls='--')


def plot_swr_event(plots, swr_event, do_texts, do_texts_right):
    """
    draw one event into the four axes of `plots` (raw, filtered, spectrogram,
    colorbar), and return its centre frequency
    """
    times = swr_event['times']
    # t = 0 is 250 ms into the event
    timeshift = times[0] + 250
    times = times - timeshift

    plot_raw(plots[0], times, swr_event['rawdata'])
    plot_filtered(plots[1], times, swr_event['filt_data'], swr_event,
                  timeshift)

    freqs = swr_event['freqs']
    plot_spectrogram(plots[2], plots[3], swr_event['stockwell'], freqs)

    if do_texts_right:
        plots[2].text(1.45, .5, 'Power [a.u.]', va='center', ha='right',
                      rotation=90, transform=plots[2].transAxes)

    if do_texts:
        for plot, text in zip(plots, YLABELS):
            plot.text(-.3, .5, text, rotation=90, va='center', ha='right',
                      transform=plot.transAxes)

    return centre_frequency(freqs, swr_event['stockwell_mean'])
