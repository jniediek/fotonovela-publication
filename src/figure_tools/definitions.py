import re
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

NAME_ANONYMIZATION = {
    # politicians
    'Donald Trump': '[US Politician]',
    'Edmund Stoiber': '[German Politician]',
    # sportspeople
    'Michael Schumacher': '[Racing\nDriver]',
    'Sebastian Vettel': '[Racing\nDriver]',
    'Mesut Özil': '[German\nFootball Player]',
    'Wesley Sneijder': '[Dutch\nFootball Player]',
    # actors and TV hosts
    'Pamela Anderson': '[Actress]',
    'Maria Furtwängler': '[Actress]',
    'Harrison Ford': '[Actor 2]',
    'Jorge García': '[Actor 1]',
    'Stefan Raab': '[TV Host 2]',
    'Thomas Gottschalk': '[TV Host 1]',
    # clinic staff (Professor Elger is a co-author and keeps his name)
    'Ms. Weisskirchen': '[Clinical Staff Member Ms. W]',
    'Weisskirchen': 'W',
    'Jenny Faber': '[Doctor F]',
    # fictional characters
    'Tyrion Lannister': '[TV\nCharacter]',
    'Lois Griffin': '[Cartoon\nCharacter]',
    'Apu': '[Cartoon\nCharacter]',
    # brand
    'an IKEA store': 'a [furniture store]',
    'IKEA store': '[furniture store]',
    'IKEA': '[Furniture store]',
}

_NAME_PATTERN = re.compile(
    r'\b(' + '|'.join(re.escape(name) for name in
                      sorted(NAME_ANONYMIZATION, key=len, reverse=True))
    + r')\b')


def anonymize(text, multiline=False):
    """Replace real names in text that is drawn into a figure.

    Replacements may contain a preferred line break; it is kept only if
    multiline is True, otherwise it becomes a space."""
    def replace(match):
        label = NAME_ANONYMIZATION[match.group(1)]
        return label if multiline else label.replace('\n', ' ')
    return _NAME_PATTERN.sub(replace, text)


def two_line_label(text):
    """Break a label at the space closest to its middle."""
    spaces = [i for i, c in enumerate(text) if c == ' ']
    if not spaces:
        return text
    i = min(spaces, key=lambda s: abs(2 * s - len(text)))
    return text[:i] + '\n' + text[i + 1:]
