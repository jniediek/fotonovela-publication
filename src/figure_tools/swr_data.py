import numpy as np

from figure_tools.definitions import DATA_DIR

FOLDER_SWR = DATA_DIR / "swr_events"


def load_swr_event(name):
    return np.load(FOLDER_SWR / (name + '.npz'))
