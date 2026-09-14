"""
Concatenate the per-figure p-value tables into one `figures/all_pvalues.csv`.

Each `plot_fig_<NAME>.py` writes a `<NAME>_pvalues.csv` next to its figure,
holding one row per statistical annotation it draws (plus the tests it computes
but does not draw, marked `drawn=False`). This script collects them for writing
the figure legends. Run it after the figure scripts, or with `--run` to run
them first.
"""
import argparse
import subprocess
import sys
from pathlib import Path

import pandas as pd

from figure_tools.definitions import FIGURE_DIR
from figure_tools.pvalue_log import COLUMNS

SCRIPT_DIR = Path(__file__).resolve().parent

# the figures that draw no statistical annotation at all
WITHOUT_STATS = ('fig_02', 'fig_S_01', 'fig_S_03_04', 'fig_S_05', 'fig_S_08')


def run_figure_scripts():
    for script in sorted(SCRIPT_DIR.glob('plot_fig_*.py')):
        if script.stem.replace('plot_', '') in WITHOUT_STATS:
            continue

        print(f'Running {script.name}')
        subprocess.run([sys.executable, script], check=True,
                       stdout=subprocess.DEVNULL)


def main(do_run):
    if do_run:
        run_figure_scripts()

    tables = sorted(FIGURE_DIR.glob('fig_*_pvalues.csv'))

    if not tables:
        raise SystemExit(f'no per-figure tables in {FIGURE_DIR}, run the '
                         'figure scripts first (or pass --run)')

    # `round_trip` keeps the last digits of a p-value across the read
    frame = pd.concat([pd.read_csv(table, float_precision='round_trip')
                       for table in tables], ignore_index=True)

    for col in ('n1', 'n2'):
        frame[col] = frame[col].astype('Int64')

    ordered = ([col for col in COLUMNS if col in frame.columns] +
               [col for col in frame.columns if col not in COLUMNS])

    target = FIGURE_DIR / 'all_pvalues.csv'
    frame[ordered].to_csv(target, index=False)

    drawn = frame.drawn.sum()
    print(f'Wrote {len(frame)} p-values from {len(tables)} figures to {target}')
    print(f'{drawn} of them are drawn in a figure, {len(frame) - drawn} are '
          'computed but not annotated')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true',
                        help='run every figure script first')
    main(parser.parse_args().run)
