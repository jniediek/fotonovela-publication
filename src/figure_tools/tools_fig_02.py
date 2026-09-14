STAGEDICT = {'1': -1, '2': -2, '3': -3,
             'R': 0, 'W': 1, '0': 2, '?': 2}

COLOR_LINES = (0, 0, .5)

COLOR_LEARN = "#30ea67"
COLOR_SCR_E = "#f0a324"
COLOR_SCR_M = "#f0a324"
COLOR_RECALL = "#49a0ed"

def nlx_to_mpl(data, nlx_start, mpl_start):
    return (data - nlx_start)/(1000 * 60 * 60 * 24) + mpl_start

