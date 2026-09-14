import numpy as np
import pandas as pd

from figure_tools.definitions import DATA_DIR

FOLDER_RIPPLES = DATA_DIR / "ripples"

FNAME_SWR_RATES = FOLDER_RIPPLES / "swr_rates_and_freqs.csv"

FNAME_BINDING = FOLDER_RIPPLES / "ripple_binding_data.npz"


def swr_info_name(pat, ses, chan):
    return '{:03d}fn{}_CSC{:02d}'.format(pat, ses, chan)


def load_swr_rates():
    """
    one row per channel and sleep stage
    """
    return pd.read_csv(FNAME_SWR_RATES, float_precision='round_trip')


def load_swr_info(pat, ses, chan):
    """
    one row per ripple of one channel
    """
    return pd.read_csv(FOLDER_RIPPLES / (swr_info_name(pat, ses, chan) + '.csv'),
                       float_precision='round_trip')


def load_binding_data():
    """
    effect size of the firing-rate change during ripples, per class and stage
    """
    return np.load(FNAME_BINDING)
