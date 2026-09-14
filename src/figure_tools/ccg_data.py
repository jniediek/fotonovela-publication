import numpy as np
import pandas as pd

from figure_tools.definitions import DATA_DIR
from figure_tools.population import load_population

FOLDER_CCG = DATA_DIR / "ccg"

FNAME_EXAMPLE = FOLDER_CCG / "example_704fn1.npz"

# the parameter tables of the sub-stages, read by FigS11
FOLDER_SPECIAL = FOLDER_CCG / "special_stages"

# the parts of a night FigS11 draws, per sleep stage
SPECIAL_PARTS = {'3': ['31', '32'],
                 'W': ['e_fn_l', 'e_fn_r', 'e_pre', 'e_scr_pre_fn',
                       'W1', 'W2']}

STAGES = 'WR3'


def correct_regions_in_frames(df_pairs, df_single):

   df = df_pairs.merge(df_single[['Region', 'ident']], left_on='ident_1', right_on='ident',
               validate='m:1', how='outer', indicator=True)
   df = df[df['_merge'] != 'right_only']
   df['Region1_pre'] = df['Region1']
   df['Region1'] = df['Region'] # this comes from the merge
   df = df.drop(columns=['Region', 'ident', '_merge'])

   df = df.merge(df_single[['Region', 'ident']], left_on='ident_2', right_on='ident',
               validate='m:1', how='outer', indicator=True)
   df = df[df['_merge'] != 'right_only']
   df['Region2_pre'] = df['Region2']
   df['Region2'] = df['Region'] # this comes from the merge
   df = df.drop(columns=['Region', 'ident'])

   df = df[df['_merge'] == 'both'].drop(columns=['_merge'])

   # At this point, the regions have been fixed quite easily and sanely
   return df.copy()


def ident_func(row, num):
   ch = row[f'Channel{num}']
   sign = row['Sign']
   clus = row[f'Cluster{num}']
   ret = f'{row.Patient:03d}_{row.Session:02d}_{ch:03d}_sort_{sign}_joh_{clus:02d}'
   return ret


def read_csvs() -> pd.DataFrame:
   all_dfs = []

   for region in ('A', 'H', 'PHC'):
      for stage in STAGES:
         fname = f'All_ccg_parameters_{stage}_stage_binned_{region}.csv'
         df = pd.read_csv(FOLDER_CCG / fname)
         df['stage'] = df['stage'].astype(str)
         all_dfs.append(df)
   df = pd.concat(all_dfs)
   df = df.reset_index(drop=True)

   for i in (1, 2):
      df[f'ident_{i}'] = df.apply(ident_func, axis=1, args=[i])

   # need to insert corrected regions here
   df_for_reg = load_population()
   df = correct_regions_in_frames(df, df_for_reg)

   # define hippocampus as region H
   idx = df.Region1.isin(('AH', 'MH', 'PH')) & df.Region2.isin(('AH', 'MH', 'PH'))
   df['Region'] = 'None'
   df.loc[idx, 'Region'] = 'H'
   idx = (df.Region1 == 'A') & (df.Region2 == 'A')
   df.loc[idx, 'Region'] = 'A'
   idx = (df.Region1 == 'PHC') & (df.Region2 == 'PHC')
   df.loc[idx, 'Region'] = 'PHC'

# append ripple data
   appn = [df]
   for stage in 'W3':
      fname = f'All_ccg_parameters_{stage}_highend_intersection.csv'
      tdf = pd.read_csv(FOLDER_CCG / fname)
      tdf['stage'] = tdf['stage'].astype(str)
      tdf['Patient'] = tdf['Patient'].astype(int)

      for i in (1, 2):
         tdf[f'ident_{i}'] = tdf.apply(ident_func, axis=1, args=[i])

      tdf = correct_regions_in_frames(tdf, df_for_reg)

      idx = tdf.Region1.isin(('AH', 'MH', 'PH')) & tdf.Region2.isin(('AH', 'MH', 'PH'))

      tdf = tdf[idx]
      tdf['Region'] = 'HRipp'
      appn.append(tdf)


   df = pd.concat(appn)
   df = df.reset_index(drop=True)

   idx = (df.Region1 != df.Region1_pre) | (df.Region2 != df.Region2_pre)
   print(f'Changed {idx.sum()} pairs in regional correction')

   df = df.loc[df.utype != 'is_inv'].reset_index(drop=True)
   # this makes sure that we don't have "same micro" stuff
   assert((df.Channel1 == df.Channel2).sum() == 0)

   pop = df_for_reg

   idx_selective = pop.is_selective & pop.is_consistent
   ident_sel = pop.ident[idx_selective]
   df['is_selective'] = False
   idx_selec = (df.ident_1.isin(ident_sel) & df.ident_2.isin(ident_sel))
   df.loc[idx_selec, 'is_selective'] = True

   # at this point we would like to add the preferred stimulus also
   df2 = df.merge(pop[['ident', 'preferred_stim_num']], left_on='ident_1', right_on='ident', validate='m:1')
   df2 = df2.rename(columns={'preferred_stim_num': 'preferred_stim_num_1'})

   df3 = df2.merge(pop[['ident', 'preferred_stim_num']], left_on='ident_2', right_on='ident', validate='m:1')
   df3 = df3.rename(columns={'preferred_stim_num': 'preferred_stim_num_2'})
   df3 = df3.drop(columns=['ident_x', 'ident_y'])

   idx = df3.is_selective
   df3.loc[~idx, 'stim_dist'] = np.nan
   df3.loc[idx, 'stim_dist'] = df3['preferred_stim_num_1'] - df3['preferred_stim_num_2']

   # add an identifier for pairs
   df3['ident_pairs'] = df3[['ident_1', 'ident_2']].agg('_'.join, axis=1)

   df3 = df3.reset_index(drop=True)

   return df3


def read_csvs_extra() -> pd.DataFrame:
   # reads data related to experiment time points (scr, learning, etc)

   all_dfs = []
   parts = SPECIAL_PARTS
   for region in ('A', 'PHC', 'H'):
      for stage in parts.keys():
         for part in parts[stage]:
            fname = f'All_ccg_parameters_{stage}_{part}_stage_binned_{region}.csv'
            df = pd.read_csv(FOLDER_SPECIAL / fname)
            df['stage'] = df['stage'].astype(str)
            df['Patient'] = df['Patient'].astype(int)
            df['timepoint'] = part
            all_dfs.append(df)

   df = pd.concat(all_dfs)

   for i in (1, 2):
      df[f'ident_{i}'] = df.apply(ident_func, axis=1, args=[i])


   df_for_reg = load_population()
   df = correct_regions_in_frames(df, df_for_reg)

   df = df.loc[df.utype != 'is_inv'].reset_index(drop=True)

   idx = df.Region1.isin(('AH', 'MH', 'PH')) & df.Region2.isin(('AH', 'MH', 'PH'))
   df['Region'] = 'None'
   df.loc[idx, 'Region'] = 'H'
   idx = (df.Region1 == 'A') & (df.Region2 == 'A')
   df.loc[idx, 'Region'] = 'A'
   idx = (df.Region1 == 'PHC') & (df.Region2 == 'PHC')
   df.loc[idx, 'Region'] = 'PHC'


   pop = df_for_reg

   idx_selective = pop.is_selective & pop.is_consistent
   ident_sel = pop.ident[idx_selective]
   df['is_selective'] = False
   idx_selec = (df.ident_1.isin(ident_sel) & df.ident_2.isin(ident_sel))
   df.loc[idx_selec, 'is_selective'] = True

   # at this point we would like to add the preferred stimulus also
   df2 = df.merge(pop[['ident', 'preferred_stim_num']], left_on='ident_1', right_on='ident', validate='m:1')
   df2 = df2.rename(columns={'preferred_stim_num': 'preferred_stim_num_1'})

   df3 = df2.merge(pop[['ident', 'preferred_stim_num']], left_on='ident_2', right_on='ident', validate='m:1')
   df3 = df3.rename(columns={'preferred_stim_num': 'preferred_stim_num_2'})
   df3 = df3.drop(columns=['ident_x', 'ident_y'])

   idx = df3.is_selective
   df3.loc[~idx, 'stim_dist'] = np.nan
   df3.loc[idx, 'stim_dist'] = df3['preferred_stim_num_1'] - df3['preferred_stim_num_2']
   # add an identifier for pairs
   df3['ident_pairs'] = df3[['ident_1', 'ident_2']].agg('_'.join, axis=1)

   df3 = df3.reset_index(drop=True)

   return df3


def load_ccg_example():
    """
    the summed cross-correlograms of the sample pair, per stage
    """
    return np.load(FNAME_EXAMPLE)
