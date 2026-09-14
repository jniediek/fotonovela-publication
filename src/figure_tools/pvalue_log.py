from contextlib import contextmanager

import pandas as pd

from figure_tools.definitions import FIGURE_DIR

# the columns in the order the CSV writes them; a keyword that is not listed
# here is still recorded, and lands in a column after these
COLUMNS = ('figure', 'panel', 'region', 'stage', 'neuron_class', 'timepoint',
           'group', 'comparison', 'test', 'alternative', 'n1', 'n2',
           'statistic', 'p', 'stars', 'drawn')

# the columns that identify an annotation rather than describe its outcome
VALUE_COLUMNS = ('n1', 'n2', 'statistic', 'p', 'stars')

ROWS = []

CONTEXT = {}


@contextmanager
def context(**fields):
    """
    add `fields` to every row recorded inside the block. A script uses this for
    what the shared plotting function it calls cannot know by itself: the name
    of the figure, and the region or neuron class the caller is looping over.
    """
    previous = CONTEXT.copy()
    CONTEXT.update(fields)

    try:
        yield
    finally:
        CONTEXT.clear()
        CONTEXT.update(previous)


def record(pval, stars=None, **where):
    """
    append one annotation. `where` names the panel and the loop variables that
    place it, plus the test, its alternative, the group sizes and the test
    statistic.
    """
    row = dict(CONTEXT)
    row.update(where)

    if 'figure' not in row:
        raise ValueError(f'p-value recorded outside a figure context: {row}')

    row['p'] = pval
    row['stars'] = stars
    row.setdefault('drawn', True)

    ROWS.append(row)


def write(name):
    """
    write the rows collected so far to `figures/<name>_pvalues.csv` and reset,
    so that a script drawing several figures gets one table per figure.
    """
    if not ROWS:
        print(f'No p-values recorded for {name}, writing no table')
        return

    from figure_tools.plot_stats import _pstars

    frame = pd.DataFrame(ROWS)
    ROWS.clear()

    for _, row in frame.iterrows():
        if pd.isna(row.stars):
            continue

        if row.stars != _pstars(row.p):
            raise ValueError(f'stars do not match the p-value: {dict(row)}')

    id_columns = [col for col in frame.columns if col not in VALUE_COLUMNS]
    duplicated = frame.duplicated(subset=id_columns, keep=False)

    if duplicated.any():
        raise ValueError('these annotations cannot be told apart, they need '
                         f'more context:\n{frame[duplicated]}')

    # group sizes are counts, and stay counts when a row leaves one of them out
    for col in ('n1', 'n2'):
        if col in frame.columns:
            frame[col] = frame[col].astype('Int64')

    ordered = ([col for col in COLUMNS if col in frame.columns] +
               [col for col in frame.columns if col not in COLUMNS])

    FIGURE_DIR.mkdir(exist_ok=True)
    target = FIGURE_DIR / f'{name}_pvalues.csv'
    frame[ordered].to_csv(target, index=False)
    print(f'Wrote {len(frame)} p-values to {target}')
