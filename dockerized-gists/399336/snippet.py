# Mixpanel, Inc.
# http://mixpanel.com

max_ring_size = 2**127

def token_percent(token, max):
    return round(token / float(max_ring_size), 4)
    
def calc(ring_load):
    highest = {'total': 0, 'percent0': 0, 'percent1': 0}
    ringarr = sorted(ring_load.items())
    prev_ring = {'percent': token_percent(*ringarr[-1]), 'load': ringarr[-1][1]}
    for token, load in ringarr:
        percent_location = token_percent(token, load)

        print 'Percent: %f \tLoad: %f' % (percent_location, load)
    
        if load > highest.get('total'):
            highest['total'] = load
            highest['percent0'] = prev_ring['percent']
            highest['percent1'] = percent_location
        prev_ring = {'percent': percent_location, 'load': load}

    mid = highest['percent1'] - highest['percent0']
    if mid < 0:
        mid = -1 * ((100 * mid) % 100) / 200.
        position = (mid + 1)
    else:
        position = highest['percent0'] + mid / 2.
        
    suggested_token = position * max_ring_size    
        
        
        
    print 'Suggested token: %d' % int(suggested_token), '@ %f' % (position * 100)
    print 'Calculated position: %f' % (suggested_token / max_ring_size * 100)

if __name__ == "__main__":
    # Update this with your token range + load
    # Eventually you can just automate this by asking nodetool for it.
    current_load = {
        1: 58.34,
        42535295865117307932921825928971026432: 51.06,
        76305956592808183638182472153122355584: 80.06,
        102084710076281535261119195933814292480: 69.25,
        127605887595351923798765477786913079296: 68.65,
        21267647932558653966460912964485513216: 51.09,
        148873535527910577765226390751398592512: 52.67,
    }
    calc(current_load)
