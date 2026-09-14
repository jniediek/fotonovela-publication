import numpy as np

from figure_tools.definitions import DATA_DIR

FOLDER_SCREENING = DATA_DIR / "screening_extra"


def load_screening(name):
    """
    read extra screening data, returns (list of trials, spike times for ISIs)
    """
    data = np.load(FOLDER_SCREENING / (name + '.npz'))
    bounds = np.cumsum(data['raster_lengths'])[:-1]
    return np.split(data['raster_times'], bounds), data['isi_times']
