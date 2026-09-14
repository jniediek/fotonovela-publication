import numpy as np
import matplotlib.pyplot as mpl
import matplotlib.cm as cm

from figure_tools.make_border_dict import make_border_dict
from figure_tools.plot_recall import plot_recall

T_PRE = 1000
T_POST = 2000
ISI_BINS = np.arange(0, 100, 2)
ISI_BINS_INSET = np.arange(0, 10, 1)

from figure_tools.tools_fig_02 import (STAGEDICT, COLOR_LINES, COLOR_LEARN,
        COLOR_SCR_E, COLOR_SCR_M, COLOR_RECALL)
from figure_tools.definitions import FOLDER_STIM_PICTURES
from figure_tools.unit_data import SPIKE_YLIM

COLORMAP = cm.viridis


def spike_heatmap(ax, density, bins, x, log=False):
    """
    plots the waveform density (see unit_data.spike_density) as a heatmap
    """
    imdata = np.log(1 + density) if log else density

    ydiff = (bins[1] - bins[0])/2.
    extent = [x[0], x[-1], bins[0]-ydiff, bins[-1]-ydiff]

    ax.imshow(imdata,
              cmap=COLORMAP,
              interpolation='hanning',
              aspect='auto',
              origin='lower',
              extent=extent)

    ax.set_xlim((x[0], x[-1]))
    
        
    ax.set_xticks((0, 1))
    ax.set_yticks((0, 100))
    ax.set_xticklabels(('0', '1 ms'), ha='left')  
    ax.text(-.05, 1, u'µV', transform=ax.transAxes, va='top', ha='right')
 

def make_raster_plots(fig, pos, has_morning):
    """
    creates the subplots for the screening information
    """
    
    box_left, box_bottom, box_width, box_height = pos
    
    # transform the bottom and the height to make room for recall
    recall_height_fraction = .3

    full_box_bottom = box_bottom
    full_box_height = box_height
    box_bottom = box_bottom + recall_height_fraction*box_height
    box_height = (1-recall_height_fraction)*box_height
    height_recall = .23*full_box_height

    if has_morning:
        morning_factor = .7 
    else:
        morning_factor = 1
    
    width_raster = width_image = 3/8 - 1/20
    height_raster = 2/3
    height_image = 1/4
    left_raster_name = 3/8
    left_other_data = 3/4
    width_other_data = 1/4
    height_other_data = 1/3
    gap_other_data = 1/20
 
    width_isi = (width_other_data - gap_other_data) * box_width
    height_isi = height_other_data * box_height * morning_factor

     
    pos_raster_image = [box_left, box_bottom,
                        box_width * width_raster, box_height * height_raster * morning_factor]

    pos_raster_name = [box_left + left_raster_name * box_width, box_bottom, box_width * width_raster,
                       box_height * height_raster * morning_factor]

    if has_morning:
        pos_raster_image_mo = [box_left, box_bottom + pos_raster_image[3], box_width * width_raster,
            box_height * height_raster * (1- morning_factor)]
        pos_raster_name_mo = [box_left + left_raster_name * box_width, box_bottom + pos_raster_name[3],
            box_width * width_raster, box_height * height_raster * (1 - morning_factor)]

        pos_isi_mo_scr = [box_left + (left_other_data + gap_other_data) * box_width,
        box_bottom + pos_raster_image[3], width_isi, 
        box_height * height_raster * (1-morning_factor)]
        pos_isi_mo_scr_inset = [pos_isi_mo_scr[0] + .6 * width_isi,
        pos_isi_mo_scr[1] + .4 * height_isi,
        .4*width_isi, .4*height_isi]


    pos_image = [box_left,
                 box_bottom + height_raster * box_height * 1.1,
                 width_image * box_width,
                 height_image * box_height *.9]

    pos_name = [box_left + left_raster_name * box_width,
                box_bottom + height_raster * box_height * 1.1,
                width_image * box_width,
                height_image * box_height *.9]
    pos_isi_mo = [box_left + (left_other_data + gap_other_data) * box_width,
                  box_bottom, width_isi, height_isi]

    pos_isi_mo_inset = [pos_isi_mo[0] + .6 * width_isi, pos_isi_mo[1] + .4 * height_isi,
            .4 * width_isi, .4 * height_isi]
    
    pos_isi_ev = [box_left + (left_other_data + gap_other_data) * box_width,
                  box_bottom + height_isi, 
                  width_isi, height_isi]

    pos_isi_ev_inset = [pos_isi_ev[0] + .6 * width_isi, pos_isi_ev[1] + .4 * height_isi,
            .4 * width_isi, .4 * height_isi]
    

    
    pos_density = [box_left + (left_other_data + gap_other_data) * box_width,
                  box_bottom + (2 * height_other_data + 2 * gap_other_data) * box_height,
                  (width_other_data - gap_other_data) * box_width,
                  (height_other_data - 2 * gap_other_data) * box_height]
    
    pos_raster_recall = [box_left, full_box_bottom + height_recall/2,
             box_width, height_recall/2.15]

    pos_hist_recall = [box_left, full_box_bottom, box_width, height_recall/2.15]
                         
    
    plots = {}
    plots['image'] = fig.add_axes(pos_image)
    plots['name'] = fig.add_axes(pos_name)
    
    plots['isi_mo'] = fig.add_axes(pos_isi_mo)
    plots['isi_ev'] = fig.add_axes(pos_isi_ev)
    plots['isi_mo_inset'] = fig.add_axes(pos_isi_mo_inset)
    plots['isi_ev_inset'] = fig.add_axes(pos_isi_ev_inset)
    plots['density'] = fig.add_axes(pos_density)
    
    plots['raster_image'] = fig.add_axes(pos_raster_image)
    plots['raster_name'] = fig.add_axes(pos_raster_name)
    
    plots['raster_recall'] = fig.add_axes(pos_raster_recall)
    plots['hist_recall'] = fig.add_axes(pos_hist_recall)

    if has_morning:
        plots['raster_image_mo'] = fig.add_axes(pos_raster_image_mo)
        plots['isi_mo_scr'] = fig.add_axes(pos_isi_mo_scr)
        plots['isi_mo_scr_inset'] = fig.add_axes(pos_isi_mo_scr_inset)

    
    for pname in ('image', 'name'):
        plots[pname].axis('off')
        p = plots['raster_' + pname]
        p.set_xticks([-T_PRE, 0, 1000, T_POST])
        p.set_xticklabels(['', 0, '1000 ms', ''])
        p.xaxis.set_label_coords(.5, -0.1, transform=p.transAxes)

   
    for pname in ('image', 'name', 'image_mo'):
        keyname = 'raster_' + pname
        if keyname not in plots:
            continue
        p = plots[keyname]
        for where in ('left', 'right', 'top', 'bottom'):
            p.spines[where].set_visible(False)
        
        for pos in (0, 1000):
            p.axvline(pos, ls='solid', color='k', lw=.5)

        p.set_xlim([-T_PRE, T_POST])
        p.set_xticks([-T_PRE, 0, 1000, T_POST])
        p.set_yticks([])

    if 'raster_image_mo' in plots:
        plots['raster_image_mo'].set_xticklabels([])
        
    for pname in ('mo', 'ev', 'mo_inset', 'ev_inset', 'mo_scr', 'mo_scr_inset'): 
        keyname = 'isi_' + pname
        if keyname not in plots:
            continue
        plot = plots[keyname]
        # plot.grid(True)
        for which in ['top', 'bottom', 'left', 'right']:
            plot.spines[which].set_visible(False)
        plot.set_yticks([])
        plot.set_xticklabels([])

    for pname in ('mo', 'ev', 'mo_scr'):
        keyname = 'isi_' + pname
        if keyname not in plots:
            continue
        plot = plots[keyname]
        plot.set_xticks([0, 50, 100])
        plot.set_xlim((0, 100))

        plot = plots['isi_{}_inset'.format(pname)]
        plot.set_xticks([0, 10])
        plot.set_xlim((0, 10))


    p = plots['isi_mo']
    p.set_xticklabels([0, 50, '100 ms'])
    #p.set_xlabel('ms')
    p.xaxis.set_label_coords(.5, -0.2, transform=p.transAxes)

    p = plots['isi_mo_inset']
    p.set_xticklabels((0, '10 ms'))
    p.xaxis.set_label_coords(.5, -0.2, transform=p.transAxes)

    
    for which in ('top', 'right'):
        plots['density'].spines[which].set_visible(False)
    
    return plots


def plot_screening(plots, stimulus_frame, unit, stim, param, add_times, add_times_e):
    """
    show raster plots for screening and recall
    """
    # create the plots
    
    # load the stimulus picture and name
    border_dict = make_border_dict(stimulus_frame)
    stimframe = stimulus_frame.copy()
    stimframe = stimulus_frame[(stimulus_frame['stim_num'] == stim) &
                                stimulus_frame['paradigm'].isin(('scr', 'nscr'))]
    
    scr_pre_idx = stimframe.time <= border_dict['e_scr_pre_fn'][1]
    stimframe.loc[scr_pre_idx, 'daytime'] = 'e_pre'
    
    scr_post_idx = ((stimframe.time >= border_dict['e_scr_post_fn'][0]) &
                    (stimframe.time <= border_dict['e_scr_post_fn'][1]))
    stimframe.loc[scr_post_idx, 'daytime'] = 'e_post'
    
    stimname = stimframe['stim_name'].values[0].replace(' ', '\n')
    
    # write the name
    plots['name'].text(.5, .5, stimname,
        transform=plots['name'].transAxes, ha='center', va='center',
        family='Verdana', size=param['stimname_size'])
    
    # show the image
    fname = FOLDER_STIM_PICTURES / stimframe['filename'].values[0]

    try:
        image = mpl.imread(fname)
        plots['image'].imshow(image, interpolation='none')
    except IOError:
        print('Image not loaded: {}'.format(fname))
    
    
    # these are the rasters
    empty = [3500]
    
    for pname, scrtype in (('image', 'scr'), ('name', 'nscr')):
        plot = plots['raster_' + pname]
        
        rows = []
        n_per_type = []
        
        for daytime in ('e_pre', 'e_post', 'm'):
            idx = ((stimframe['daytime'] == daytime) &
                   (stimframe['paradigm'] == scrtype))
            
            if not idx.any():
                continue
            
            onset_times = stimframe.loc[idx, 'time'].to_numpy()
            
            for onset_time in onset_times:
                idx = ((unit['times'] >= onset_time - T_PRE) &
                       (unit['times'] <= onset_time + T_POST))
                if idx.any():
                    rows.append(unit['times'][idx] - onset_time)
                else:
                    rows.append(empty)
            
            if 'e' in daytime: 
                rows += [empty]
                n_per_type.append(onset_times.shape[0] + 1)
            else:
                n_per_type.append(onset_times.shape[0] + 1)
            
        rows.reverse()
        plot.eventplot(rows, colors=[COLOR_LINES] * len(rows), linewidths=.7)
        
        shifts = (0, n_per_type[0], sum(n_per_type[:2]), sum(n_per_type))
        
        for yshift in shifts:
            plot.axhline(len(rows) - yshift, xmin=-.1, color='grey', lw=.5, clip_on=False)
        
        if pname == 'image':
            for pos, suffix in ((5/6, 'Day 1\nEvening'), (3/6, 'Day 1\nEvening'), (1/6, 'Day 2\nMorning')):
                plot.text(-.12, pos, suffix, transform=plot.transAxes,
                          va='center', ha='center', color=COLOR_SCR_E,
                          rotation=90)
            plot.text(-.3, .5, 'Mini-screenings', transform=plot.transAxes,
                      va='center', rotation=90, ha='right', weight='bold', color=COLOR_SCR_E)
               
        plot.set_ylim((-1, len(rows)))
    
    if add_times is not None:
        plot = plots['raster_image_mo']
        rows = []
        for item in add_times:
            if item.any():
                rows.append(item)
            else:
                rows.append([-5000])

        plot.eventplot(rows, colors=[COLOR_LINES] * len(rows), linewidths=.7)
        plot.text(-.12, 1/2, 'Day 1\nMorning', transform=plot.transAxes,
        va='center', ha='center', color=COLOR_SCR_E, rotation=90)
        plot.text(-.3, 1/2, 'Screening', transform=plot.transAxes,
        va='center', ha='center', color=COLOR_SCR_E, rotation=90, weight='bold')




    # now the ISI histogram
    start_stops = (('ev', border_dict['e_scr_pre_fn'][0],
        border_dict['e_scr_post_fn'][1]),
                    ('mo', border_dict['m_fn'][0],
                        border_dict['m_scr_post_fn'][1]))
    names = {'ev': 'Day 1\nEvening',
             'mo': 'Day 2\nMorning'}
    for name, start_t, stop_t in start_stops:
        t_idx = (unit['times'] >= start_t) & (unit['times'] <= stop_t)
        t_diff = np.diff(unit['times'][t_idx])
        t_diff = t_diff[t_diff <= 100]
        
        # do the plot only if there is something in it
        if not t_diff.shape[0]:
            continue
            
        hist, _ = np.histogram(t_diff, ISI_BINS)
        plot = plots['isi_' + name]
        plot.bar(ISI_BINS[:-1], hist, width=2,
            edgecolor='none', facecolor=COLOR_LINES)
        plot.text(-.3, .5, names[name], transform=plot.transAxes,
                rotation=90, va='center', ha='center')


        # as per reviewer request, do the 10 ms inset
        hist, _ = np.histogram(t_diff[t_diff <= 10], ISI_BINS_INSET)
        plot = plots['isi_{}_inset'.format(name)]
        plot.bar(ISI_BINS_INSET[:-1], hist, width=1,
                edgecolor='none', facecolor=COLOR_LINES)
        plot.axvline(3, color='darkred', lw=.5, ymax=.5)
        stat = (t_diff <= 3).sum()/t_diff.shape[0]
        plot.text(-.5, 1, '{:.1%} < 3 ms'.format(stat),
                transform=plot.transAxes, size=6)

    if add_times_e is not None:
        plot = plots['isi_mo_scr']
        t_diff = np.diff(add_times_e)
        t_diff = t_diff[t_diff <= 100]
        plot.text(-.3, .5, 'Day 1\nMorning', transform=plot.transAxes,
                rotation=90, va='center', ha='center')


        if t_diff.any():
            hist, _ = np.histogram(t_diff, ISI_BINS)
            plot.bar(ISI_BINS[:-1], hist, width=2,
            edgecolor='none', facecolor=COLOR_LINES)
            hist, _ = np.histogram(t_diff[t_diff <= 10], ISI_BINS_INSET)
            plot = plots['isi_mo_scr_inset'.format(name)]
            plot.bar(ISI_BINS_INSET[:-1], hist, width=1,
                    edgecolor='none', facecolor=COLOR_LINES)
            plot.axvline(3, color='darkred', lw=.5, ymax=.5)
            stat = (t_diff <= 3).sum()/t_diff.shape[0]
            plot.text(-.5, 1, '{:.1%} < 3 ms'.format(stat),
                    transform=plot.transAxes, size=6)

    # density plot
    spike_heatmap(plots['density'], unit['density'],
            unit['density_bins'], unit['density_x'])
    plots['density'].set_ylim(SPIKE_YLIM)

    # after everything else, the recall plot
    stimframe = stimulus_frame.copy()
    idx = ((stimframe.daytime == 'e') &
           (stimframe.stim_num == stim) &
           (stimframe.paradigm == 'right'))
    stimframe = stimframe.loc[idx, :] 
    onset_times = stimframe.time.to_numpy()
    plot_recall(plots['raster_recall'], plots['hist_recall'],
            unit['times'], onset_times, param)

    plots['raster_recall'].text(-.12, .5, 'Recall',
            transform=plots['raster_recall'].transAxes, va='center',
            rotation=90,
            ha='center', weight='bold',
            color=COLOR_RECALL)
    plots['raster_recall'].text(-.05, .5, 'Day 1\nEvening',
    transform=plots['raster_recall'].transAxes, va='center',
    ha='center', color=COLOR_RECALL, rotation=90)
