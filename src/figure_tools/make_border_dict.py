def make_border_dict(frame, do_debug=False):
    """
    create dict of border times
    
    you supply the stimulus frame as an argument

    key e_fn_l refers to morning learning
    key e_fn_r refers to morning recall

    same for morning
    """
    ret = dict()
    frame = frame.sort_values(by='time')

    e_idx = frame.daytime == 'e'
    m_idx = frame.daytime == 'm'

    scr_idx = frame.paradigm.isin(['scr', 'nscr'])
    fn_idx = ~scr_idx

    fn_l_idx = frame.paradigm.isin(['learn'])
    fn_r_idx = fn_idx & ~fn_l_idx

    ret['e_fn'] = (frame.loc[e_idx & fn_idx, 'time'].values.min(),
                   frame.loc[e_idx & fn_idx, 'time'].values.max())

    ret['e_fn_l'] = (frame.loc[e_idx & fn_l_idx, 'time'].values.min(),
                     frame.loc[e_idx & fn_l_idx, 'time'].values.max())

    ret['e_fn_r'] = (frame.loc[e_idx & fn_r_idx, 'time'].values.min(),
                     frame.loc[e_idx & fn_r_idx, 'time'].values.max())


    pre_e_fn_idx = frame.time <= ret['e_fn'][0]
    post_e_fn_idx = frame.time >= ret['e_fn'][-1]

    if (e_idx & pre_e_fn_idx & scr_idx).any():
        ret['e_scr_pre_fn'] = (frame.loc[e_idx & scr_idx, 'time'].values.min(),
                           frame.loc[e_idx & pre_e_fn_idx & scr_idx, 'time'].values.max())
    else:
        ret['e_scr_pre_fn'] = None

    if (e_idx & scr_idx & post_e_fn_idx).any() and (e_idx & scr_idx).any():
        ret['e_scr_post_fn'] = (frame.loc[e_idx & scr_idx & post_e_fn_idx, 'time'].values.min(),
                                frame.loc[e_idx & scr_idx, 'time'].values.max())
    else:
        # print('No e_scr_post_fn')
        ret['e_scr_post_fn'] = None

    if (m_idx & fn_idx).any():
        ret['m_fn'] = (frame.loc[m_idx & fn_idx, 'time'].values.min(),
                       frame.loc[m_idx & fn_idx, 'time'].values.max())

        if (m_idx & fn_l_idx).any():
            ret['m_fn_l'] = (frame.loc[m_idx & fn_l_idx, 'time'].values.min(),
                             frame.loc[m_idx & fn_l_idx, 'time'].values.max())

        if (m_idx & fn_r_idx).any():
            ret['m_fn_r'] = (frame.loc[m_idx & fn_r_idx, 'time'].values.min(),
                             frame.loc[m_idx & fn_r_idx, 'time'].values.max())


        # pre_m_fn_idx should be nothing except for a few cases
        pre_m_fn_idx = frame.time <= ret['m_fn'][0]
        post_m_fn_idx = frame.time >= ret['m_fn'][-1]

        if (m_idx & scr_idx & pre_m_fn_idx).any():
            ret['m_scr_pre_fn'] = (frame.loc[m_idx & scr_idx, 'time'].values.min(),
                               frame.loc[m_idx & scr_idx & pre_m_fn_idx, 'time'].values.max())

            print('Morning screening conducted before fn, duration: {:.1f} s'.format(
                (ret['m_scr_pre_fn'][1] - ret['m_scr_pre_fn'][0])/1000))

        else:
            # print('No m_scr_pre_fn')
            ret['m_scr_pre_fn'] = None

        if (m_idx & scr_idx & post_m_fn_idx).any():
            ret['m_scr_post_fn'] = (frame.loc[m_idx & scr_idx & post_m_fn_idx, 'time'].values.min(),
                                    frame.loc[m_idx & scr_idx, 'time'].values.max())
    else:
        for key in ('fn', 'scr_pre_fn', 'scr_post_fn'):
            ret['m_' + key] = None

    for key in sorted(ret):

        val = ret[key]

        if (val is None):
            if do_debug:
                print('{}: does not exist'.format(key))
            continue

        if val[1] <= val[0]:
            ret[key] = None

        if do_debug:
            if ret[key] is None:
                print('{}: does not exist'.format(key))
            else:
                print('{}: {:.1f} min'.format(key, (val[1] - val[0])/6e4))

    return ret
