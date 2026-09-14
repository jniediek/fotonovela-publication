import numpy as np
import pandas as pd
import matplotlib.pyplot as mpl
from matplotlib.gridspec import GridSpec
from scipy.stats import fisher_exact

from figure_tools.definitions import FIG_WIDTH_FULL, FIGURE_DIR
from figure_tools.population import ANALYZED_SESSIONS, load_population
from figure_tools import pvalue_log
from figure_tools.style import set_paper_style, save_figure, SIZE_LABEL, TYPE_COLORS, TYPE_NAMES
from figure_tools.unit_counts import get_unit_counts

# panel A shows every region, panels B and C only the analysed ones
ALL_REGIONS = ('A', 'PHC', 'EC', 'H')
ANALYSIS_REGIONS = ('A', 'PHC', 'H')

SHORT_NAMES = {'A': 'Amyg.', 'H': 'Hipp.', 'EC': 'Ent.', 'PHC': 'Parahipp.'}

EDGE_COLOR = 'k'
EDGE_LW = .2

COLORS = ('#ff7f0e', '#1f77b4', '#2ca02c')
LIGHT_COLORS = ('#ffae66', '#8ebad9', '#95cf95')

BBOX_VALUE = (-.1, 1.05)

# the panel letters are set larger than the manuscript-wide letter size
SIZE_LETTERS = 18


def label_diff(plot, transform, x1, x2, y, text):
    """
    draw a bracket between two bars and label it

    inspired by http://stackoverflow.com/a/11543637
    """
    props = {'arrowstyle': '-', 'shrinkA': 0, 'shrinkB': 0,
             'lw': .8, 'color': 'k'}

    plot.text((x1 + x2)/2, y, text, zorder=10, ha='center', va='bottom',
              transform=transform)

    for f1, f2, f3 in ((x1, x2, y), (x1, x1, y - 1), (x2, x2, y - 1)):
        plot.annotate('', xy=(f1, y), xytext=(f2, f3), arrowprops=props,
                      xycoords=transform, textcoords=transform)


def prepare_plot(plot):
    for pos in ('top', 'right'):
        plot.spines[pos].set_visible(False)
    plot.yaxis.grid(True)
    plot.set_axisbelow(True)


def plot_response_counts(plot, data):
    """
    panel A: channels and units per region, responsive ones highlighted
    """
    basic = np.linspace(0, .6, 3)
    plot.set_ylabel('Counts')
    plot.set_xticks(basic[1] + np.arange(len(data)))
    plot.set_xticklabels([SHORT_NAMES[reg] for reg in ALL_REGIONS])

    for i_reg, region in enumerate(ALL_REGIONS):
        n_ch, n_mu, n_mu_r, n_su, n_su_r = data[region]

        plot.bar(basic[0] + i_reg, n_ch, width=.6/2,
                 color=COLORS[0], edgecolor=EDGE_COLOR, lw=EDGE_LW)
        plot.bar(basic[1:] + i_reg, [n_mu, n_su], width=.6/2,
                 color=LIGHT_COLORS[1:], edgecolor=EDGE_COLOR, lw=EDGE_LW)
        plot.bar(basic[1:] + i_reg, [n_mu_r, n_su_r], width=.6/2,
                 color=COLORS[1:], edgecolor=EDGE_COLOR, lw=EDGE_LW)

        for i_bar, numbers in enumerate(((n_ch,), (n_mu, n_mu_r),
                                         (n_su, n_su_r))):
            for number in numbers:
                plot.text(basic[i_bar] + i_reg + .15/4, number, ' ' + str(number),
                          ha='center', va='bottom', rotation=90)

    # the legend entries are drawn as bars outside the x-limits
    legend_labels = ('Recording channels',
                     'Multi-units (total)', 'Multi-units (responsive)',
                     'Single-units (total)', 'Single-units (responsive)')
    for color, alpha, label in zip(
            (COLORS[0], COLORS[1], COLORS[1], COLORS[2], COLORS[2]),
            (1, .5, 1, .5, 1), legend_labels):
        plot.bar(-1, 0, color=color, alpha=alpha, label=label)

    plot.legend(loc=3, fontsize=SIZE_LABEL, bbox_to_anchor=BBOX_VALUE, ncol=1)
    plot.set_xlim((-.2, len(data) - .2))
    plot.set_ylim((0, 325))


def plot_percentages(plot, population):
    """
    panel B: responsive, selective and concept cells per analysed region

    Returns the selective and concept cell counts per region, which the two
    Fisher tests below are computed on.
    """
    width = .5
    xticks = (.25, 1.25, 2.25)
    plot.set_xticks(xticks)
    plot.set_xticklabels([SHORT_NAMES[reg] for reg in ANALYSIS_REGIONS])
    plot.set_ylabel('Counts')
    plot.set_ylim(0, 155)
    plot.set_yticks((0, 25, 50, 75, 100, 125))

    labels = ('Responsive neurons', 'Selective neurons', 'Concept cells')
    colors = ('#fa5984', TYPE_COLORS['resp'], TYPE_COLORS['inv'])

    number_store = {}

    for i_reg, region in enumerate(ANALYSIS_REGIONS):
        reg_idx = population.Simple_Region == region
        resp = reg_idx & population.is_resp
        selective = reg_idx & population.is_selective & population.is_consistent
        inv = reg_idx & population.is_inv & population.is_consistent

        number_store[region] = (selective.sum(), inv.sum())

        for i_bar, idx in enumerate((resp, selective, inv)):
            label = labels[i_bar] if i_reg == 0 else None
            n_units = idx.sum()
            plot.bar(i_reg, n_units, width=width, color=colors[i_bar],
                     edgecolor=EDGE_COLOR, align='edge', label=label,
                     lw=EDGE_LW)
            # the selective bar is the tallest, its label needs more room
            offset = 8 if i_bar == 1 else 1
            plot.text(i_reg + width, n_units - offset, f'{n_units}',
                      ha='left', va='top')

    plot.legend(loc=3, bbox_to_anchor=BBOX_VALUE, fontsize=SIZE_LABEL)

    comparisons = ((('A', 'PHC'), xticks[0], xticks[1] - .02),
                   (('PHC', 'H'), xticks[1] + .02, xticks[2]))

    for (left, right), x1, x2 in comparisons:
        OR, pval = fisher_exact(np.array([number_store[left],
                                          number_store[right]]))
        pvalue_log.record(pval,
                comparison=f'{SHORT_NAMES[left]} vs {SHORT_NAMES[right]}',
                test='fisher_exact', alternative='two-sided', statistic=OR)
        label_diff(plot, plot.transData, x1, x2, 145, 'p = {:.5f}'.format(pval))

    return number_store


def plot_by_patient(plot, population):
    """
    panel C: non-responsive, selective and concept cells per patient

    Returns the per-session counts, which are written out alongside the figure.
    """
    no_ec_idx = population.Region != 'EC'
    selective_idx = population.is_selective & population.is_consistent
    inv_idx = population.is_inv & population.is_consistent

    print('Panel C plots {} selective units and {} concept cells'.format(
        (selective_idx & no_ec_idx).sum(), (inv_idx & no_ec_idx).sum()))

    patients = population.Patient.unique()

    for i_pat, pat in enumerate(patients):
        idx = (population.Patient == pat) & no_ec_idx
        n_all = idx.sum()
        n_selective = (idx & selective_idx).sum()
        n_inv = (idx & inv_idx).sum()

        # stacked from the bottom: everything else, selective, concept cells
        heights = {'no_resp': n_all - n_selective,
                   'resp': n_selective - n_inv,
                   'inv': n_inv}
        bottoms = {'no_resp': 0,
                   'resp': n_all - n_selective,
                   'inv': n_all - n_inv}

        for label, height in heights.items():
            name = TYPE_NAMES[label]
            plot.bar(i_pat + 1, height, bottom=bottoms[label],
                     color=TYPE_COLORS[label],
                     label=name[0].upper() + name[1:] if i_pat == 0 else None)

    plot.set_xticks(range(1, len(patients) + 1))
    plot.set_xticklabels(range(1, len(patients) + 1))
    plot.set_xlim((.5, len(patients) + .5))
    plot.set_xlabel('Patient No.')
    plot.set_ylabel('Counts')
    plot.legend(ncol=3, loc='upper left', bbox_to_anchor=(-.01, 1.25))

    return session_table(population, patients, selective_idx, inv_idx,
                         no_ec_idx)


def session_table(population, patients, selective_idx, inv_idx, no_ec_idx):
    """
    the number of concept cells and selective neurons per session

    Sessions are numbered in the order they were analysed, patients by their
    position in panel C rather than by their real number.
    """
    patient_number = {pat: i_pat + 1 for i_pat, pat in enumerate(patients)}

    rows = []
    for i_ses, (pat, ses) in enumerate(ANALYZED_SESSIONS):
        idx = (population.Patient == pat) & (population.Session == ses)
        rows.append((i_ses + 1, patient_number[pat],
                     (idx & inv_idx & no_ec_idx).sum(),
                     (idx & selective_idx & no_ec_idx).sum()))

    return pd.DataFrame(rows, columns=['Session No.', 'Patient No.',
                                       '# concept cells',
                                       '# selective neurons'])


def do_plot():
    fig = mpl.figure(figsize=(FIG_WIDTH_FULL, 5))
    grid = GridSpec(2, 2, left=.1, bottom=.1, right=.97, top=.7, wspace=.3,
                    hspace=.5, width_ratios=[3, 2])

    plots = {job: fig.add_subplot(grid[0, i]) for i, job in enumerate('AB')}
    plots['C'] = fig.add_subplot(grid[1, :])

    x = {'A': .02, 'B': .6, 'C': .02}
    y = {'A': .95, 'B': .95, 'C': .38}

    for letter, plot in plots.items():
        fig.text(x[letter], y[letter], letter.lower(), weight='bold',
                 size=SIZE_LETTERS)
        prepare_plot(plot)

    population = load_population()

    plot_response_counts(plots['A'], get_unit_counts(population))

    with pvalue_log.context(figure='fig_S_02', panel='b'):
        numbers = plot_percentages(plots['B'], population)
    print('Panel B, (selective, concept cells) per region: {}'.format(numbers))
    print('{} selective neurons, {} concept cells'.format(
        sum(x[0] for x in numbers.values()),
        sum(x[1] for x in numbers.values())))

    table = plot_by_patient(plots['C'], population)

    FIGURE_DIR.mkdir(exist_ok=True)
    pvalue_log.write('fig_S_02')
    save_figure(fig, 'fig_S_02', dpi=300)
    table.to_csv(FIGURE_DIR / 'session_unit_stats.csv', index=False)


if __name__ == '__main__':
    set_paper_style()
    do_plot()
