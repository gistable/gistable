def to_ts(x):
        return time.mktime(time.strptime(x, '%Y-%m-%d %H:%M:%S'))
    
data_trams['time'] = data_trams['time'].apply(to_ts)