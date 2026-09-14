import matplotlib.pyplot as mpl
from matplotlib.colors import hsv_to_rgb

from figure_tools.definitions import FIGURE_DIR

PAPER_RC_PARAMS = {
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial'],
    'font.size': 7,
    'mathtext.fontset': 'custom',
    'mathtext.rm': 'Arial',
    'mathtext.it': 'Arial',
    # the journal wants the text in the vector files editable, so embed the
    # fonts as TrueType instead of matplotlib's Type 3 default
    'pdf.fonttype': 42,
}

# resolution of the bitmaps (heatmaps, spectrograms, photographs) that a vector
# file embeds, the journal asks for at least 300
PDF_DPI = 600


# the response classes of figure_tools.population, wherever they are drawn
TYPE_COLORS = {
    'no_resp': '#574d43',
    'resp': '#cc295f',
    'inv': '#29b1cc',
}

# the one-letter abbreviations used as tick labels
TYPE_LETTERS = {
    'no_resp': 'N',
    'resp': 'S',
    'inv': 'C',
}

TYPE_NAMES = {
    'no_resp': 'non-responsive neurons',
    'resp': 'selective neurons',
    'inv': 'concept cells',
}

# the sleep stages a figure draws, as (hue in degrees, saturation, value)
STAGE_COLORS = {
    '3': hsv_to_rgb((220/360, 1, .65)),
    'R': hsv_to_rgb((5/360, 1, .94)),
    'W': hsv_to_rgb((120/360, 1, .50)),
}

# the same stages, for filled areas behind text
STAGE_COLORS_PALE_2 = {
    '3': '#7f9ad2',
    'R': '#f7897f',
    'W': '#7fbf7f',
}

# the halves of the night, drawn by FigS11
STAGE_COLORS['31'] = STAGE_COLORS_PALE_2['31'] = '#536fa6'
STAGE_COLORS['32'] = STAGE_COLORS_PALE_2['32'] = '#9dbaf2'

STAGE_LONGNAMES = {
    '3': 'SWS',
    'R': 'REM',
    'W': 'Awake',
}

# legends and other in-axes labels are set one point above the body text
SIZE_LABEL = 8

# boxplot outliers, wherever a figure draws a boxplot
flierprops = {
    'marker': '.',
    'fillstyle': 'full',
    'markersize': 2,
    'markeredgecolor': 'grey',
}

# the bars of Fig07 panel d, and the lines of its panel c
STAGE_HATCHES = {'R': None, '3': None, 'W': None}
LW_LINE = .9


def set_paper_style():
    """
    apply the manuscript-wide rcParams, call once at the start of a script
    """
    mpl.rcParams.update(PAPER_RC_PARAMS)


def save_figure(fig, name, dpi=300, pdf_dpi=PDF_DPI):
    """
    write the figure twice: the PDF that goes to the journal and the PNG the
    port is reviewed against. `dpi` applies to the PNG, `pdf_dpi` to the
    bitmaps the otherwise vector PDF embeds. A figure with a rasterized artist
    whose appearance depends on the resolution (the amplitude cloud of
    plot_timeline) passes the dpi of its reference figure as `pdf_dpi`.
    """
    FIGURE_DIR.mkdir(exist_ok=True)

    for target in (FIGURE_DIR / f'{name}.pdf', FIGURE_DIR / f'{name}.png'):
        fig.savefig(target, dpi=pdf_dpi if target.suffix == '.pdf' else dpi)
        print(f'Saved figure {target}')
