import numpy as np

from figure_tools.definitions import TYPE_MU, TYPE_SU

# the fields of the array returned per region, in order
COUNT_FIELDS = ('n_ch', 'n_mu', 'n_mu_r', 'n_su', 'n_su_r')


def get_unit_counts(population):
     # a channel is identified by the session it was recorded in
    channel = (population.Patient.map(str) + population.Session.map(str) +
               population.Channel.map(str))

    idx_mu = population.Type == TYPE_MU
    idx_su = population.Type == TYPE_SU
    idx_resp = (population.n_resp_scr_e + population.n_resp_scr_m) > 0

    counts = {}
    for region in population.Simple_Region.unique():
        idx = population.Simple_Region == region
        counts[region] = np.array((
            channel[idx].nunique(),
            (idx & idx_mu).sum(),
            (idx & idx_mu & idx_resp).sum(),
            (idx & idx_su).sum(),
            (idx & idx_su & idx_resp).sum(),
        ))

    return counts
