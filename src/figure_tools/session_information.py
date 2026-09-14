import os
from collections import namedtuple
import csv
import numpy as np
from scipy.io import loadmat
import pandas as pd
from figure_tools.definitions import DATA_DIR
from figure_tools.parse_datetime import parse_datetime
DEBUG = True

FOLDER_SLEEPSTAGES = DATA_DIR / "sleepstages"
FOLDER_INFO = DATA_DIR / "session_info"

SessionInfo = namedtuple('Session',
    ['patient',
     'session',
    #  'cluster_data',
    #  'response_data',
    #  'responses_per_unit',
     'stimulus_frame',
    #  'channel_names',
     'sleepstages',
    #  'pvalue_frame',
     'start_nlx',
     'stop_nlx',
     'start_datetime',
     'stop_datetime',
     'infix',
    #  'cluster_frame',
    #  'pvalue_frame_transformed',
    #  'fs_downsampled',
     'continuous_start',
     'continuous_stop',
     'analysis_window',])
    #  'has_nscr',
    #  'spike_folder',
    #  'rawdata_folder'])

use_python_3 = True


SLEEPSTAGE_DTYPE = np.dtype([('starttime', float),
                             ('stoptime', float),
                             ('stage', 'U1')])


def read_sleepstages(fname):
    raw = loadmat(fname)['sleepstages'].ravel()

    stages = np.empty(raw.shape[0], dtype=SLEEPSTAGE_DTYPE)
    for name in ('starttime', 'stoptime', 'stage'):
        stages[name] = [entry.ravel()[0] for entry in raw[name]]

    return stages


def read_channel_names(fname):
    with open(fname, 'r') as fid:
        data = {int(l[0][3:]) : l[1]
                for l in csv.reader(fid, delimiter=';')}
    return data


def channel_names(pat, ses):
    infix = '{:03d}fn{}'.format(pat, ses)
    return read_channel_names(os.path.join(FOLDER_INFO, infix,
                                           'channel_names.csv'))


def read_session_info(pat, ses):
    """
    Read information for one session
    """
    infix = '{:03d}fn{}'.format(pat, ses)
    this_folder_sleepstages = os.path.join(FOLDER_SLEEPSTAGES, infix)
    this_folder_info = os.path.join(FOLDER_INFO, infix)

    response_data = None
    responses_per_unit = None

    # read list of stimulus presentations
    fname_frame = os.path.join(FOLDER_INFO, infix,
            "frame_{}".format(infix))
    stimulus_frame = pd.read_json(fname_frame + '.json')

    # read sleep stage data
    fname_sleepstages = os.path.join(this_folder_sleepstages,
                                     "{}_sleepstages.mat".format(infix))
    try:
        sleepstages = read_sleepstages(fname_sleepstages)
    except IOError as error:
        # print(error)
        sleepstages = None

    # Read open/close time. First check if a total_time file exists,
    # else read from sleepstage folder
    fname_total = os.path.join(this_folder_info,
            '{}_total_start_stop.txt'.format(infix))
    if os.path.isfile(fname_total):
        print('Reading absolute start/stop datetime')

        start_nlx, start_datetime, stop_nlx, stop_datetime = parse_datetime(fname_total)

    else:
        fname_open_close = os.path.join(this_folder_sleepstages,
                                        "start_stop_datetime.txt")
        try:
            start_nlx, start_datetime, stop_nlx, stop_datetime = parse_datetime(fname_open_close)
        except IOError as error:
            print(error)

    fname_continuous = os.path.join(this_folder_info, '{}_continuous_start_stop.txt'.format(infix))
    if os.path.isfile(fname_continuous):
        print('Reading start/stop datetime of longest continuous piece')
        cont_start, _, cont_stop, _ = parse_datetime(fname_continuous)

    else:
        cont_start = start_nlx
        cont_stop = stop_nlx

    # define the time window for sleep-related analyses
    if (sleepstages is None) or (stimulus_frame is None):
        analysis_window = None
    else:
        start_staging = sleepstages['starttime'][0]
        stop_staging = sleepstages['stoptime'][-1]

        latest_e = stimulus_frame.loc[stimulus_frame.daytime == 'e', 'time'].max()
        first_m = stimulus_frame.loc[stimulus_frame.daytime == 'm', 'time'].min()

        a_start = np.max((start_staging, cont_start, latest_e))
        a_stop = np.min((stop_staging, cont_stop, first_m))

        analysis_window = np.array((a_start, a_stop)).ravel()
    this_session = SessionInfo(pat, ses, stimulus_frame, sleepstages, start_nlx,
            stop_nlx, start_datetime, stop_datetime, infix, cont_start,
            cont_stop, analysis_window)

    return this_session


def story_stimuli(stimulus_frame, daytime):
    idx = ((stimulus_frame.paradigm == 'right') &
           (stimulus_frame.daytime == daytime) &
           stimulus_frame.stim_num.notnull())

    frame = stimulus_frame[idx]

    stimuli = []

    for stim_num, rows in frame.groupby('stim_num'):
        rows = rows.sort_values('time')
        stimuli.append({'stim_num': stim_num,
                        'stim_name': rows.stim_name.values[0],
                        'filename': rows.filename.values[0],
                        'times': rows.time.values})

    stimuli.sort(key=lambda stim: stim['times'][0])

    return stimuli


if __name__ == "__main__":
    info = read_session_info(717, 2)