import matplotlib.pyplot as mpl

from figure_tools.definitions import FIG_WIDTH_FULL, FONT_SIZE_LETTERS
from figure_tools.session_information import read_session_info, story_stimuli
from figure_tools.plot_story_timeline import plot_story_timeline
from figure_tools.style import save_figure, set_paper_style
from figure_tools.unit_data import load_unit

PATIENT, SESSION = 704, 1

# the story was told six times in the evening block
DAYTIME = 'e'

# the units shown, one figure each, with the slide the raster is aligned to
# (unit, target index, letter, name)
SAMPLES = (
    ('CSC9_pos_03', 3, 'a', 'fig_S_05_a'),
    ('CSC9_pos_01', 5, 'b', 'fig_S_05_b'),
)


def plot_timeline(unit_name, target_index, letter, name):

    info = read_session_info(PATIENT, SESSION)
    stimuli = story_stimuli(info.stimulus_frame, DAYTIME)
    unit = load_unit('{}_{}'.format(info.infix, unit_name))

    fig = mpl.figure(figsize=(FIG_WIDTH_FULL, FIG_WIDTH_FULL/2.6))
    plot_story_timeline(fig, stimuli, unit['times'], target_index)

    fig.text(.005, .99, letter, va='top', size=FONT_SIZE_LETTERS, weight='bold')

    save_figure(fig, name)
    mpl.close(fig)


if __name__ == '__main__':
    set_paper_style()
    for sample in SAMPLES:
        plot_timeline(*sample)
