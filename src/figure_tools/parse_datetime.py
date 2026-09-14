import datetime

def parse_datetime(fname):
    """
    read datetime file
    returns ts_start_nlx: start time in milliseconds
    ts_start_mpl: start time as datetime object
    """

    with open(fname, 'r') as fid:
        lines = [line.strip() for line in fid.readlines()]

    for line in lines:
        if line[0] == '#':
            continue
        fields = line.split()

        if fields[0] in ('start_recording', 'stop_recording'):
            dtime, micro = fields[2].split('.')
            dstr = fields[1] + ' ' + dtime
            dfmt = '%Y-%m-%d %H:%M:%S'
            date = datetime.datetime.strptime(dstr, dfmt)
            date += datetime.timedelta(microseconds=int(micro))
            ts_nlx = float(fields[3])/1000

            if fields[0] == 'start_recording':
                start_date = date
                ts_start_nlx = ts_nlx

            elif fields[0] == 'stop_recording':
                stop_date = date
                ts_stop_nlx = ts_nlx


    return ts_start_nlx, start_date, ts_stop_nlx, stop_date

