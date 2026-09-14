import numpy as np

from figure_tools.definitions import DATA_DIR

FOLDER_COUNT_CORR = DATA_DIR / "count_corr"

FNAME_TIMECOURSE = FOLDER_COUNT_CORR / "timecourse_704fn1.npz"


def load_cc_data(name):
    return np.load(FOLDER_COUNT_CORR / (name + '.npz'))


def load_cc_timecourse():
    return np.load(FNAME_TIMECOURSE)
