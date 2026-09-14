import numpy as np
import pandas as pd

from figure_tools.definitions import DATA_DIR

FOLDER_SLEEP = DATA_DIR / "sleep_frates"

FNAME_SLEEP_FRATES = FOLDER_SLEEP / "sleep_frates_total.csv"

FOLDER_SLEEP_BINS = DATA_DIR / "sleep_bins"


def load_sleep_frates():
    return pd.read_csv(FNAME_SLEEP_FRATES)


def load_sleep_bins(pat, ses):
    infix = '{:03d}fn{}'.format(pat, ses)
    return np.load(FOLDER_SLEEP_BINS / (infix + '.npz'))
