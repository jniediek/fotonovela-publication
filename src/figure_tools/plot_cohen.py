import numpy as np
import scipy.stats
from matplotlib.transforms import blended_transform_factory

from figure_tools.definitions import LONGNAMES
from figure_tools.plot_stats import label_diff, pstars
from figure_tools.sleep_data import load_sleep_bins
from figure_tools.style import (flierprops, STAGE_COLORS, STAGE_COLORS_PALE_2,
                                STAGE_LONGNAMES)

STAGES = ('3', 'W', 'R')
BOX_WIDTH=.4
flierprops['markersize'] = 1.5


def spines_off(plot):
    for pos in ('right', 'top'):
        plot.spines[pos].set_visible(False)

    plot.set_xticklabels([])
    plot.yaxis.grid(True)
    plot.set_axisbelow(True)


def cohen_d(samp1, samp2):
    """
    Cohen's d, taken from
    https://en.wikipedia.org/wiki/Effect_size#Cohen.27s_d

    see also http://stackoverflow.com/a/26809325
    """
    n1 = samp1.shape[0]
    n2 = samp2.shape[0]

    assert n1 > 1
    assert n2 > 1

    var1 = np.var(samp1, ddof=1)
    var2 = np.var(samp2, ddof=1)

    if (var1 == 0) and (var2 == 0):
        print('Variance is Zero!')
        return np.nan
    ssquared = ((n1 - 1) * var1 + (n2 - 1)*var2)/(n1 + n2 - 2)

    return (samp1.mean() - samp2.mean())/np.sqrt(ssquared)


def draw_cohen_bars(fig, pos, info, ch, sign, clus, check_data):
    plot = fig.add_axes(pos)
    bins = load_sleep_bins(info.patient, info.session)
    idx = ((check_data.Patient == info.patient) &
           (check_data.Session == info.session) &
           (check_data.Channel == ch) &
           (check_data.Sign == sign) &
           (check_data.Cluster == clus))
    print(check_data.loc[idx, ('Cohen_W3', 'Cohen_WR')])

    fr_line = bins['{:02d}_sort_{}_joh_{:02d}'.format(ch, sign, clus)]
    stg = bins['stages'][:-1]
    tline = bins['bins'][:-1]
    exclude = ((tline <= info.analysis_window[0]) |
        (tline >= info.analysis_window[1]))
    include = ~exclude
    print('Excluding {}'.format(np.sum(exclude)))

    res = dict()
    cds = dict()

    plot.set_ylabel('Mean firing-rate\nin sleep stage [Hz]')
    spines_off(plot)

    for stage in STAGES:
        idx = (stg == stage) & include
        res[stage] = fr_line[idx]

    for cstage in ('R', '3'):
        cds[cstage] = cohen_d(res[cstage], res['W'])
        print('{}: {}'.format(cstage, cds[cstage]))

    transform = blended_transform_factory(plot.transData, plot.transAxes)

    xshift = 1
    plot.set_xticks([])
    pdata = [res[x] for x in STAGES]
    boxes = plot.boxplot(pdata, positions=[0, 1, 2], notch=True, patch_artist=True,
             flierprops=flierprops, widths=BOX_WIDTH)
    for box, color in zip(boxes['boxes'], [STAGE_COLORS_PALE_2[st] for st in STAGES]):
        box.set_facecolor(color)

    for i, st in enumerate(STAGES):
        n = len(res[st])
        #plot.bar(i, res[st].mean(), edgecolor=None,
                # color=STAGE_COLORS_PALE_2[st])
        print('Sample unit: {} mean {} ste {}'.format(st, res[st].mean(),
            res[st].std()/np.sqrt(len(res[st]))))

        plot.text(i, 1.01, f'{n}', #' x\n10 sec.'.format(n),
                color='k', ha='center', va='bottom', transform=transform)

        # this adds the stage names
        text = STAGE_LONGNAMES[st]
        plot.text(i * xshift + (xshift-1)/2, -.06, text,
                    color=STAGE_COLORS[st],
                    weight='bold', ha='center',
                    va='top', transform=transform)

    plot.set_xticklabels([])
    plot.yaxis.grid(True)
    plot.set_axisbelow(True)
    plot.text(-.7, 1.01, 'N (bins) = ', ha='center', va='bottom', transform=transform,
    weight='bold')

    # plot.errorbar(range(len(STAGES)), [res[st].mean() for st in STAGES],
            # [res[st].std()/np.sqrt(len(res[st])) for st in STAGES]
            # ls='none', color='k', marker=',')

    plot.text(.5, 1.22, 'Modulation of a\nsample concept cell', ha='center',
            transform=plot.transAxes, weight='bold', va='top')

    pos = {'3': .9, 'R': 0.9}
    for pair in ('3W3W', 'RWWR'):
        p1, p2, p1p, p2p = pair
        c1 = cohen_d(res[p1], res[p2])
        label_diff(plot, transform, STAGES.index(p1p), STAGES.index(p2p),
                pos[p1], 'd = {:.2f}'.format(c1), move_inner=.05)


def draw_stats(plots_dots, plots_perc, data, reg_idxs, regions,
        concept_idx, params):

    if params['label_long']:
        dotsylabelshift = -.15
        barylabelshift = -.3
        dotslabel = 'Mean firing rate\nin sleep stage [Hz]'
        barlabel = 'Direction of modulation\n[% units]'

    else:
        dotsylabelshift = -.55
        barylabelshift = -.4
        dotslabel = 'Firing rate [Hz]'
        barlabel = r'% units'

    if params['do_heading']:
        do_heading = True
        dotsheading = 'Mean firing rate\nin sleep stage [Hz]'
        barheading = 'Direction of\nmodulation'
    else:
        do_heading = False
        barheading = None
        dotsheading = None

    ypos_N = params['ypos_N']

    at = (u'↓', u'≈', u'↑')
    xshift = 1

    for pl in (plots_dots, plots_perc):
        for p in pl:
            spines_off(p)

    all_tables = {}

    mean_fr_stats = list()
    comparison_stats = list()
    fisher_stats = list()

    for i_reg, reg in enumerate(regions):

        plot = plots_dots[i_reg]
        plot_perc = plots_perc[i_reg]
        Ns = []

        transform = blended_transform_factory(plot.transData,
                plot.transAxes)
        transform_perc = blended_transform_factory(plot_perc.transData,
            plot_perc.transAxes)

        # retrieve the data for this region
        select_idx = reg_idxs[reg] & concept_idx

        this_data = data.loc[select_idx, ('M_3', 'M_W', 'M_R')]
        Ns.append(this_data.shape[0])

        mean_fr_row = [params['invariant_name'], reg, this_data.shape[0]]

        for row in this_data.values:
            plot.plot((0, 1, 2), row, lw=.5, color='k', alpha=.5)

        max_fr = 0
        for istg, stage in enumerate(STAGES):
            stage_data = this_data.loc[:, 'M_' + stage]
            max_fr = np.max([max_fr, stage_data.max()])
            plot.plot(istg + np.zeros(this_data.shape[0]),
                    stage_data, ls='none',
                    marker='.', color=STAGE_COLORS[stage], alpha=1,
                    markeredgewidth=0)
            plot.text(istg, ypos_N, f'{stage_data.shape[0]}',
                      ha='center',
                      transform=transform)
            plot.text(istg, 1.01, f'{stage_data.mean():.1f}',
                    ha='center',
                    transform=transform)
            mean_fr_row += [stage_data.mean(), stage_data.std()]


            if (i_reg == 0) and params['stats_do_xtext']:
                text = STAGE_LONGNAMES[stage]

                plot.text(istg * xshift + (xshift-1)/2, -.06, text,
                    color=STAGE_COLORS[stage],
                    weight='bold', ha='center',
                    va='top', transform=transform,
                    rotation=params['stage_angle'])

        if i_reg == 0:
            plot.text(-.2, 1.01, 'mean f.r. = ', ha='right',
            transform=transform, weight='bold')
            plot.text(-.2, ypos_N, f'N = ', ha='right',
                      transform=transform, weight='bold')
            if params['do_titles']:
                plot.text(.5, 1.2, 'Hippocampal concept cells',
                        transform=plot.transAxes, weight='bold', ha='center', va='top')

        mean_fr_stats.append(mean_fr_row)

        fisher_table = np.zeros((2, 2))

        for ipair, pair in enumerate(('3W3W', 'RWWR')):

            p1, p2, p1p, p2p = pair

            this_data2 = data.loc[select_idx, 'Cohen_' + p2 + p1]
            idx1 = (this_data2 < -.2)
            idx2 = (this_data2 > .2)
            idx3 = ~idx1 & ~idx2
            N = this_data2.shape[0]
            comparison_row = [params['invariant_name'], reg, N, p1, p2]

            counts = np.array((0, idx2.sum(), idx3.sum(), idx1.sum()))
            plot_data = counts/N*100
            for name, number in zip(('lower', 'higher', 'same'),
                    (idx1.sum(), idx2.sum(), idx3.sum())):
                print("In {} {} {}/{} units ({:.1%}) had {} firing rates".
                    format(LONGNAMES[reg], p1, number, N, number/N, name))

            p_binom = scipy.stats.binomtest(idx1.sum(), idx1.sum() + idx2.sum())
            print('Binomial test: {:.6g}'.format(p_binom.pvalue))
            fisher_table[ipair, :] = (idx1.sum(), idx2.sum())

            if (i_reg == 0) and params['stats_do_xtext']:
                text = STAGE_LONGNAMES[p1]

                plot_perc.text(ipair, -.06, text,
                        color=STAGE_COLORS[p1],
                        weight='bold', ha='center',
                        va='top', transform=transform_perc)

            plot_perc.text(ipair, 1.01, pstars(p_binom.pvalue,
                    panel=params.get('panel_perc'), region=LONGNAMES[reg],
                    neuron_class=params['invariant_name'],
                    comparison=f'{STAGE_LONGNAMES[p1]} vs {STAGE_LONGNAMES[p2]}',
                    test='binomtest', alternative='two-sided',
                    n1=idx1.sum(), n2=idx2.sum()),
                    ha='center', va='center', transform=transform_perc)

            for i in (1, 2, 3):
                tshift = 0

                plot_perc.bar(ipair, plot_data[i],
                    bottom=sum(plot_data[:i]),
                    color=STAGE_COLORS_PALE_2[p1],
                    edgecolor='k', width=.5)

                if counts[i] < 5:
                    size = params['small_arrow_size']
                else:
                    size = 16

                textypos = sum(plot_data[:i]) + plot_data[i]/2 + tshift

                plot_perc.text(ipair, textypos,
                        at[i-1], color='k',
                        weight='bold', ha='center',
                        va='center', size=size, family='Liberation Serif')
                plot_perc.text(ipair + .26, textypos,
                        '{:>3d}'.format(counts[i]), va='center')

            [T, p] = scipy.stats.wilcoxon(this_data.M_W,
                    this_data.loc[:, 'M_' + p1])
            d_local = cohen_d(this_data.M_W, this_data.loc[:, 'M_' + p1])
            comparison_row += [d_local, T, p, p_binom.pvalue]
            comparison_stats.append(comparison_row)

            print(reg, p2, p1, 'wilcoxon', p, 'test statistic', T,
                    'N = {}'.format(len(this_data.M_W)))
            #print('Cohen\'s d: {}'.format(d_local))
            assert p2 == 'W'
            for our_p in (p1, p2):
                print(our_p, 'mean: ',
                        this_data.loc[:, 'M_' + our_p].mean(),
                        'median: ',
                        this_data.loc[:, 'M_' + our_p].median(),
                        'std: ', this_data.loc[:, 'M_' + our_p].std())
            label_diff(plot, transform, STAGES.index(p1p),
                    STAGES.index(p2p),
                    .9,  pstars(p, panel=params.get('panel_dots'),
                        region=LONGNAMES[reg],
                        neuron_class=params['invariant_name'],
                        comparison=f'{STAGE_LONGNAMES[p1]} vs {STAGE_LONGNAMES[p2]}',
                        test='wilcoxon', alternative='two-sided',
                        n1=len(this_data.M_W), statistic=T),
                    move_inner=.05) #'p = {:.5f}'.format(p))


        plot.set_xticks([])
        plot.set_ylim((0, 1.2*max_fr))
        plot.set_xlim((-.5, 2.5))
        plot_perc.set_xticks([])
        plot_perc.set_xlim(params['perc_xlim'])

        if i_reg == 0:
            plot.text(dotsylabelshift, .5, dotslabel, rotation=90,
                    transform=plot.transAxes, ha='center', va='center')
            plot_perc.text(barylabelshift, .5, barlabel, rotation=90,
                    transform=plot_perc.transAxes, ha='center', va='center')

#            plot_perc.set_ylabel(barlabel, labelpad=-1)

            if params['stats_do_xtext']:
                plot_perc.text(.5, params['stats_compare_dist'],
                        'compared to Awake',
                    color=STAGE_COLORS['W'], weight='bold', ha='center',
                    va='top', transform=transform_perc)
            if do_heading:
                plot_perc.text(.5, 1.35, barheading, ha='center',
                        va='top', transform=transform_perc)
                plot.text(.5, 1.35, dotsheading, ha='center', va='top',
                        transform=transform)

        OR, p = scipy.stats.fisher_exact(fisher_table)
        print(reg, fisher_table)
        fisher_stats.append([params['invariant_name'], reg, OR, p])
        all_tables[reg] = fisher_table
        print('Fisher\'s exact test for numbers: {:.5f} (OR = {:.2f})'
                .format(p, OR))
        label_diff(plot_perc, transform_perc, 0, 1, 1.1, pstars(p,
                panel=params.get('panel_perc'), region=LONGNAMES[reg],
                neuron_class=params['invariant_name'],
                comparison=f'{STAGE_LONGNAMES["3"]}/{STAGE_LONGNAMES["W"]} vs '
                           f'{STAGE_LONGNAMES["R"]}/{STAGE_LONGNAMES["W"]}',
                test='fisher_exact', alternative='two-sided',
                n1=fisher_table[0].sum(), n2=fisher_table[1].sum(),
                statistic=OR), move_inner=.05)

        expl = ('f.r. decreased', 'f.r. similar', 'f.r. increased')
        if params['do_titles']:
            plot_perc.text(.5, 1.2, 'Modulated neuron counts', ha='center',
                       va='top', weight='bold', transform=plot_perc.transAxes)

            mytext = '\n'.join([at[i] + ' ' + expl[i] for i in (0, 1, 2)])
            plot_perc.text(.95, .1, mytext,
                        transform=plot_perc.transAxes,
                        backgroundcolor='w')


    return all_tables, mean_fr_stats, comparison_stats, fisher_stats
