from figure_tools import pvalue_log

def pstars(pval, **where):
    stars = _pstars(pval)
    pvalue_log.record(pval, stars, **where)

    return stars


def _pstars(pval):
    """
    transforms pval into stars
    """
    if pval < .001:
        return '***'

    if pval < .01:
        return '**'

    if pval < .05:
        return '*'

    return 'n.s.'


def label_diff(plot, transform, x1, x2, y, text, move_inner=0):
    """
    annotate with p-values
    inspired by http://stackoverflow.com/a/11543637

    """

    weight = 'regular'

    if '*' in text:
        shift = .008
    else:
        shift = 0

    props = {'arrowstyle': '-',
             'shrinkA': 0,
             'shrinkB': 0,
             'lw': .8, 'color': 'k'}

    plot.text((x1 + x2)/2, y - shift, text, zorder=10,
              ha='center', va='bottom', weight=weight,
              transform=transform)

    x1_moved = x1 + move_inner
    x2_moved = x2 - move_inner

    for f1, f2, f3 in ((x1_moved, x2_moved, y),
                       (x1_moved, x1_moved, y-.01),
                       (x2_moved, x2_moved, y-.01)):

        plot.annotate('', xy=(f1, y), xytext=(f2, f3),
                      arrowprops=props, xycoords=transform,
                      textcoords=transform)
