import pandas as pd

from figure_tools.definitions import DATA_DIR

FOLDER_RECALL = DATA_DIR / "recall"

FNAME_RECALL = FOLDER_RECALL / "recall_zscores.csv"


def load_recall():
    """
    one row per (unit, stimulus), identified by `ident` and `Stim-Num`
    """
    return pd.read_csv(FNAME_RECALL)
