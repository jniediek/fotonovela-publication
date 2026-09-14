import pandas as pd

from figure_tools.definitions import DATA_DIR
from figure_tools.population import load_population

FOLDER_EMERGING = DATA_DIR / "emerging"

FNAME_EXP = FOLDER_EMERGING / "correlations_during_exp.csv"

FNAME_POST = FOLDER_EMERGING / "windowed_correlations.csv"


def load_and_merge_correlations():
    df_exp = pd.read_csv(FNAME_EXP, float_precision='round_trip')
    print(df_exp.columns)
    pop = load_population()

    idx_pop = pop.is_selective & pop.is_consistent

    df_post = pd.read_csv(FNAME_POST, float_precision='round_trip')

    # The following asserts that no regional information is carried in df_post
    assert((df_post.columns == ['ident_pairs', 'ident_1', 'ident_2', 'Corr_W1', 'Corr_W2', 'Corr_3',
       'Corr_R']).all())

    df_sel = df_post.ident_1.isin(pop.ident[idx_pop]) & df_post.ident_2.isin(pop.ident[idx_pop])
    df_post = df_post[df_sel]

    idx_hemi = (df_exp.Hemisphere_1 == df_exp.Hemisphere_2) & (df_exp.Simple_Region_1 == df_exp.Simple_Region_2)
    idx_sel = df_exp.ident_1.isin(pop.ident[idx_pop]) & df_exp.ident_2.isin(pop.ident[idx_pop])
    idx_bin_len = df_exp.bin_len < 300

    df_use = df_exp[idx_hemi & idx_sel & idx_bin_len].copy()
    df_use['pair_ident'] = df_use.apply(lambda x: f'{x.ident_1}_{x.ident_2}', axis = 1)

    use_list = df_use.pair_ident.to_list()
    data_list = df_post.ident_pairs.to_list()

    # this checks that all pairs that exist after the experiment also exist during the experiment

    diffset = (set(use_list) - set(data_list))
    probl = len(diffset)


    if probl > 0:
        idx_rem = df_use.pair_ident.isin(diffset)
        df_use = df_use[~idx_rem].copy()


    df_rec = df_use[df_use.Experiment == 'e_fn_r'].copy()
    df_pre = df_use[df_use.Experiment == 'e_pre'].copy()
    df_pre['Duration_pre'] = df_pre['Duration']
    df_rec = df_rec.merge(df_pre.loc[:, ['pair_ident', 'Duration_pre']], left_on='pair_ident', right_on='pair_ident', validate='1:1')
    df_rec = df_rec.merge(df_post, left_on='pair_ident', right_on='ident_pairs', validate='1:1')

    # now use the same technique to bring the screening and learning data into the picture
    df_rec['Corr_e_fn_r'] = df_rec['Corr']
    df_rec = df_rec.drop(columns=['Corr'])
    for col in ['e_fn_l', 'e_scr_pre_fn', 'e_scr_post_fn', 'e_pre']:
        df_rec = df_rec.merge(df_use.loc[df_use.Experiment == col, ['pair_ident', 'Corr']], left_on='pair_ident',
                              right_on='pair_ident', validate='1:1', how='outer')
        df_rec['Corr_' + col] = df_rec['Corr'].copy()
        df_rec = df_rec.drop(columns=['Corr'])

    df_all = df_rec.copy()

    return df_all
