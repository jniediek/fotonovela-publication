from pathlib import Path

FONT_SIZE_LETTERS = 12
FONT_SIZE_REGIONS = 12

FIG_WIDTH_FULL = 7.2
FIG_WIDTH_HALF = 3.5

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MATERIALS_DIR = BASE_DIR / "materials"
FIGURE_DIR = BASE_DIR / "figures"

FOLDER_PERFORMANCE = DATA_DIR / "performance"

FOLDER_STIM_PICTURES = MATERIALS_DIR / "stimulus_pictures"

LONGNAMES = {'A': 'Amyg.',
             'H': 'Hipp.',
             'PHC': 'Parahipp.',
             'HRipp': 'Hipp. ripples'}

# unit types as the spike sorter labels them
TYPE_MU = 1
TYPE_SU = 2
