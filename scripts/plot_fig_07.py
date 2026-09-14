import scipy.stats
import matplotlib.pyplot as mpl
from matplotlib.gridspec import GridSpec
import pandas as pd
import numpy as np

from figure_tools.ccg_data import read_csvs
from figure_tools.definitions import (FIG_WIDTH_FULL, FIGURE_DIR,
                                      FONT_SIZE_LETTERS, FONT_SIZE_REGIONS,
                                      LONGNAMES)
from figure_tools.plot_ccg import plot_A, plot_asymmetry, prepare_plot
from figure_tools.plot_stats import pstars
from figure_tools import pvalue_log
from figure_tools.style import (LW_LINE, save_figure, set_paper_style, STAGE_COLORS,
                                STAGE_COLORS_PALE_2, STAGE_HATCHES,
                                STAGE_LONGNAMES)

LEFT = .08
RIGHT = .98
BOTTOM_MID = .79
TOP = .91
HSPACE = .5
WSPACE = .5

STAGES = 'WR3'
REGIONS = ('A', 'PHC', 'H', 'HRipp')


def plot_decoding_panel(data, plot):

   stages = STAGES
   width = .7

   for istage, stage in enumerate(stages):
      idx = (data.stage == stage) & data['significant']
      t_data = data[idx]
      n_total = t_data.shape[0]
      if n_total == 0:
         print(Warning(f"n_total = {n_total} in stage {stage}"))
         continue
      n_coincident = t_data['coincident'].sum()
      n_wrong = (~t_data['coincident']).sum()

      binom_res = scipy.stats.binomtest(n_coincident, n_total, .5)
      print(f'In {stage}, N_total = {n_total}, N_coinc = {n_coincident},'
            f'N_wrong = {n_wrong}. {n_coincident/n_total:.1%}'
            f' forward pairs (P = {binom_res.pvalue:.3f})')


      for val, bot, facecolor in ((n_coincident/n_total, 0, True),
                                    (n_wrong/n_total, n_coincident/n_total, False)):
            edgecolor = STAGE_COLORS_PALE_2[stage]
            if facecolor:
               facecolor = edgecolor
               hatch = STAGE_HATCHES[stage]
            else:
               facecolor = 'w'
               hatch = None

            plot.bar(istage, 100*val, bottom=100*bot, width=width, align='center',
                     color='w', ec='k', fc=facecolor, hatch=hatch)

      for val, pos in ((n_coincident, 50), (n_wrong, 95)):
            plot.text(istage + width/2 + .02, pos, int(val), ha='left', va='center', weight='bold')


      binom_where = {'stage': STAGE_LONGNAMES[stage],
                     'comparison': 'forward vs reverse', 'test': 'binomtest',
                     'alternative': 'two-sided', 'n1': n_coincident,
                     'n2': n_wrong}

      if n_total > 12:
         titletext = f'{n_coincident/n_total:.1%}\n {pstars(binom_res.pvalue, **binom_where)}'
      else:
         pvalue_log.record(binom_res.pvalue, drawn=False, **binom_where)
         titletext = f'({n_coincident/n_total:.1%})\n  '

      plot.text(istage, 105, titletext, ha='center',
               va='bottom')


def plot_peaks(plot, peak_data, bins, color, ls) -> None:

   hist, _ = np.histogram(peak_data, bins)
   hist = hist.astype(float)
   hist = 100*hist/hist.sum()

   # center of each bin as x values
   x = bins[:-1] + (bins[1] - bins[0])/2

   plot.plot(x, hist, lw=LW_LINE, color=color, ls=ls)


def plot_B_and_C(fig, pos_dict_B, pos_dict_C, data, select_col):
   regions = REGIONS
   grid_B = GridSpec(1, len(regions), **pos_dict_B)
   grid_C = GridSpec(1, len(regions), **pos_dict_C)
   modenames = {'asymmetry': 'Abs. asymmetry',
                'peak': 'Pairs [%]'}

   # stats = dict()
   bin_width = 15
   peak_cutoff = 25
   peak_hist_bins = np.arange(0, 250 + bin_width, bin_width)

   # all_rows = list()
   comp_frames = list()
   # peak_rows = list()

   ylim_dict = {'H': .17,
                'A': .17,
                'PHC': .17,
                'HRipp': .5}


   for i_reg, region in enumerate(regions):

      idx_reg = data.Region == region
      idx_utype = data[select_col]
      idx_all = idx_reg & idx_utype
      if not idx_all.any():
         continue
      reg_data = data[idx_all].copy()

      if (region == 'HRipp'):
         stages = ('W', '3')
         pairs = ['W3']
      else:
         stages = ('W', 'R', '3')
         pairs = ('WR', 'R3', 'W3')

      box_xs = np.arange(len(stages)) # + (icl * len(stages))
      asym_box_data = []
      peak_data = {}
      peak_data_signif = {}

      for stage in stages:
         idx = (reg_data.stage == stage) & (reg_data.y_peak > 0)
         asym_box_data.append(reg_data.loc[idx, 'asymmetry'].abs())
         peak_data[stage] = reg_data.loc[idx, 'x_peak'].abs()
         n_pairs = idx.sum()
         idx_significant = idx & reg_data.significant
         n_signi_pairs = idx_significant.sum()
         frac = n_signi_pairs/n_pairs
         peak_data_signif[stage] = reg_data.loc[idx_significant, 'x_peak'].abs()
         print(f'In region {region} stage {stage}, have {n_pairs} pairs, {n_signi_pairs} significant ({frac:.1%})')

      plot_B = fig.add_subplot(grid_B[i_reg])
      prepare_plot(plot_B)
      title_pos_y = 1.5
      plot_B.text(.5, title_pos_y, LONGNAMES[region],
               size=FONT_SIZE_REGIONS,
               va='bottom', ha='center',
               transform=plot_B.transAxes,
               weight='bold')

      with pvalue_log.context(figure='fig_07', panel='b',
                              region=LONGNAMES[region]):
         _, t_comp_frame = plot_asymmetry(plot_B, asym_box_data,
               stages, box_xs, pairs)

      # t_comp_frame.loc[:, 'Type'] = LONG_INV_NAMES_DICT_NEW[clname]
      t_comp_frame.loc[:, 'Region'] = LONGNAMES[region]

      comp_frames.append(t_comp_frame)

      plot_B.set_xlim((-.5, len(stages) - .5))
      plot_B.set_ylim((-.001, ylim_dict[region]))

      plot_C = fig.add_subplot(grid_C[i_reg])
      prepare_plot(plot_C)

      plot_C.axvline(peak_cutoff, lw=LW_LINE, color='grey')
      plot_C.set_ylim((0, 60))
      plot_C.set_xlim((0, 200))
      plot_C.set_xlabel('Peak time [ms]')

      if i_reg == 0:
         plot_B.text(-.38, .5, modenames['asymmetry'],
                    transform=plot_B.transAxes,
                    va='center', ha='center',
                    rotation=90)
         plot_C.text(-.38, .5, modenames['peak'],
                    transform=plot_C.transAxes,
                    va='center', ha='center',
                    rotation=90)

         plot_B.text(0, 1.05, 'N =\nMean =',
                        #color=STAGE_COLORS[stage],
                        ha='right',
                        color='k',
                        transform=plot_B.transAxes)

      for istage, stage in enumerate(stages):
         # plot_peaks(plot_C, peak_data[stage], peak_hist_bins, STAGE_COLORS[stage], ls='--')
         plot_peaks(plot_C, peak_data_signif[stage], peak_hist_bins, STAGE_COLORS[stage], ls='-')

   # here we are after the loop over regions
   # the following frame returns the within-region comparison statistics
   frames = pd.concat(comp_frames)

   return frames


def plot_D(fig, pos_dict, data, select_col):
   regions = REGIONS
   grid = GridSpec(1, len(regions), **pos_dict)

   rem = data['x_peak'].abs() < 3
   data = data[~rem].copy().reset_index(drop=True)
   data.loc[:, 'coincident'] = np.sign(data['x_peak']) == np.sign(data['stim_dist'])
   idx_utype = data[select_col]

   for i_reg, region in enumerate(regions):
      print(f'Working on D region {region}')
      plot = fig.add_subplot(grid[i_reg])
      prepare_plot(plot)
      idx = (data.Region == region) & idx_utype
      reg_data = data[idx]
      with pvalue_log.context(figure='fig_07', panel='d',
                              region=LONGNAMES[region]):
         plot_decoding_panel(reg_data, plot)
      plot.set_xlim((-.5, len(STAGES) - .5))
      plot.set_xticks([])
      plot.set_yticks((0, 50))

      if i_reg == 0:
         label = r'Fwd | Rev'
         plot.text(-.2, .5, label, transform=plot.transAxes,
            ha='right', va='center', rotation=90)

         legend_pos_y = -.5
         for stage in STAGES:
            plot.bar(-10, 1,
                     color=STAGE_COLORS_PALE_2[stage],
                     lw=1,
                     label=STAGE_LONGNAMES[stage])
         plot.legend(loc='lower left',
               bbox_to_anchor=(-.2, legend_pos_y),
               ncol=3)




def create_fig_7_fabian(data, select_col):
   make_plots = ['A', 'B', 'C', 'D']

   ttop = .63
   tbot = .09
   c_shift = .03

   spacing = (ttop - tbot)/5


   fig = mpl.figure(figsize=(FIG_WIDTH_FULL, 6), dpi=200)
   pos_dict_A = {'left': LEFT, 'bottom': BOTTOM_MID,
               'right': RIGHT, 'top': TOP}

   pos_dict_B = {'left': LEFT, 'bottom': tbot+4*spacing,
               'right':RIGHT, 'top': ttop,
               'hspace': HSPACE, 'wspace': WSPACE}

   pos_dict_C = {'left': LEFT, 'bottom': tbot + 2*spacing + c_shift,
            'right': RIGHT, 'top': tbot + 3*spacing + c_shift,
            'hspace': HSPACE, 'wspace': WSPACE}
   pos_dict_D = {'left': LEFT, 'bottom': tbot,
            'right': RIGHT, 'top': tbot + 1*spacing,
            'hspace': HSPACE, 'wspace': WSPACE}

   dicts = (pos_dict_A, pos_dict_B, pos_dict_C, pos_dict_D)

   if 'A' in make_plots:
      print('\n\nPLotting part A')
      plot_A(fig, pos_dict_A)
      print('A done', end='\n\n')

   if 'B' in make_plots:
   # the frames will later be saved for manuscript
      print('\n\nPlotting B and C')
      frames = plot_B_and_C(fig, pos_dict_B, pos_dict_C, data, select_col)
      frames.to_csv(FIGURE_DIR / 'fig_07_fabian_B_C.csv', index=False)
      print('B and C done', end='\n\n')


   if 'D' in make_plots:
      print('\n\nPlotting D')
      plot_D(fig, pos_dict_D, data, select_col)
      print('D done', end='\n\n')

   for i_row, pdict in enumerate(dicts):
      top = pdict['top'] + .05
      if i_row == 2:
         top = top - c_shift
      fig.text(pdict['left'] - .07, top, 'abcd'[i_row],
               size=FONT_SIZE_LETTERS, weight='bold')

   pvalue_log.write('fig_07')
   save_figure(fig, 'fig_07', dpi=300)


def main():
   data = read_csvs()

   select_col = 'is_selective'

   FIGURE_DIR.mkdir(exist_ok=True)
   create_fig_7_fabian(data, select_col)


if __name__ == "__main__":
   set_paper_style()
   main()
