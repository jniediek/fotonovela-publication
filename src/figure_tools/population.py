import numpy as np
import pandas as pd

from figure_tools.definitions import DATA_DIR

FOLDER_POPULATION = DATA_DIR / "population"

FNAME_CLUSTER_INFO = FOLDER_POPULATION / "cluster_info.csv"

ANALYZED_SESSIONS = (
    (701, 1),
    (702, 1), (702, 3), (702, 4),
    (703, 1), (703, 2), (703, 3),
    (704, 1), (704, 2), (704, 3), (704, 4), (704, 5),
    (705, 1),
    (706, 1), (706, 2), (706, 3), (706, 4),
    (707, 1), (707, 2),
    (708, 1),
    (709, 1), (709, 2), (709, 3), (709, 4),
    (710, 1),
    (711, 1), (711, 4),
    (712, 1), (712, 2), (712, 3),
    (713, 1), (713, 2),
    (714, 1), (714, 2),
    (715, 1),
    (716, 1), (716, 2), (716, 3),
    (717, 1), (717, 2),
)

STABILITY_CUTOFF = .9

CORR_DATA = {
    708: [('LPH', 'LPHC'), ('LPHC', 'LEC'), ('RPH', 'RPHC'), ('RPHC', 'REC')],
    709: [('LMH', 'LPHC'), ('LPH', 'LPHC'), ('RAH', 'REC'), ('RMH', 'RPHC'),
          ('RPH', 'RPHC')],
    711: [('LPHC', 'LPH')],
    714: [('LA', 'LEC')],
    717: [('LPHC', 'LFFC')],
}

EXCLUDE_709FN1 = ((6, 1), (46, 1), (46, 4), (45, 4))

HIPPOCAMPUS = ('AH', 'MH', 'PH')


def correct_regions(pop):
    corrected = pop['Region'].copy()

    for pat, corrections in CORR_DATA.items():
        for old_reg, new_reg in corrections:
            # the hemisphere is a column of its own, so it is split off the
            # region label before matching
            old_hemi = old_reg[0]
            idx = ((pop.Patient == pat) & (pop.Region == old_reg[1:]) &
                   (pop.Hemisphere == old_hemi))
            corrected[idx] = new_reg[1:]

    pop = pop.copy()
    pop['Region_Original'] = pop['Region']
    pop['Region'] = corrected
    return pop


def mark_class(pop):
    pop = pop.copy()
    pop['has_any_resp'] = (pop.n_resp_scr_e + pop.n_resp_scr_m) > 0

    pop['is_resp'] = pop.has_any_resp
    pop['is_no_resp'] = ~pop.has_any_resp
    pop['is_inv'] = pop.has_any_resp & (pop.invariance_score > 0)
    pop['is_selective'] = (pop.has_any_resp & (pop.n_resp_scr_e < 2) &
                           (pop.n_resp_scr_m < 2))
    return pop


def add_preferred_stimulus(pop):
    pop = pop.copy()
    stim_e = pop['preferred_stim_num_e']
    stim_m = pop['preferred_stim_num_m']

    has_e = stim_e > -1
    has_m = stim_m > -1

    problem_idx = (has_e & has_m & (stim_e != stim_m)) | (~has_e & ~has_m)
    normal_idx = (has_e & ~has_m) | (~has_e & has_m)
    good_idx = has_e & has_m & (stim_e == stim_m)

    pop['stim_order_quality'] = np.zeros(pop.shape[0], int)
    pop.loc[problem_idx, 'stim_order_quality'] = -1
    pop.loc[normal_idx, 'stim_order_quality'] = 1
    pop.loc[good_idx, 'stim_order_quality'] = 2

    # where the two screenings agree, the evening one is used
    usable_idx = normal_idx | good_idx
    pop['preferred_stim_num'] = (-1)*np.ones(pop.shape[0], int)
    pop.loc[usable_idx & ~has_e, 'preferred_stim_num'] = stim_m
    pop.loc[usable_idx & has_e, 'preferred_stim_num'] = stim_e

    pop['is_consistent'] = pop.stim_order_quality > 0
    return pop


def load_population():
    """
    the population of sorted units, one row per unit

    Units are identified by `ident`, which is what the figure scripts merge on.
    """
    pop = pd.read_csv(FNAME_CLUSTER_INFO)

    pop = correct_regions(pop)

    channel_cluster = pd.MultiIndex.from_arrays([pop.Channel, pop.Cluster])
    del_idx = ((pop.Patient == 709) & (pop.Session == 1) &
               channel_cluster.isin(EXCLUDE_709FN1))
    assert del_idx.sum() == len(EXCLUDE_709FN1)
    pop = pop[~del_idx]

    pop = pop[pop.Region != 'FFC']

    pop = mark_class(pop)

    include_idx = ~pop.Exclude_Double & (pop.Rel_Stability >= STABILITY_CUTOFF)
    pop = pop[include_idx]

    pop['Simple_Region'] = pop.Region
    pop.loc[pop.Region.isin(HIPPOCAMPUS), 'Simple_Region'] = 'H'

    pop['Responses_Total'] = pop['n_resp_scr_e'] + pop['n_resp_scr_m']

    pop = add_preferred_stimulus(pop).reset_index(drop=True)

    # every analysed session has to be represented, and no other
    sessions = pop[['Patient', 'Session']].drop_duplicates()
    assert tuple(sessions.itertuples(index=False, name=None)) == ANALYZED_SESSIONS

    return pop
