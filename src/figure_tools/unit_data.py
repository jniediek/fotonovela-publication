import numpy as np

from figure_tools.definitions import DATA_DIR

FOLDER_UNITS = DATA_DIR / "units"

SPIKE_YLIM = (-50, 190)


def load_unit(name):
    return np.load(FOLDER_UNITS / (name + '.npz'))
