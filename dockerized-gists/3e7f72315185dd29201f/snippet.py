import numpy as np

def segment2segment_distance(a, b):
    """
    Adapted from http://geomalgorithms.com/a07-_distance.html
    """
    SMALL_NUM = 0.00000001
    S1P0 = np.array(a[:2])
    S1P1 = np.array(a[2:])
    S2P0 = np.array(b[:2])
    S2P1 = np.array(b[2:])
    u = S1P1-S1P0
    v = S2P1-S2P0
    w = S1P0-S2P0
    a = np.dot(u,u)
    b = np.dot(u,v)
    c = np.dot(v,v)
    d = np.dot(u,w)
    e = np.dot(v,w)
    
    D = a*c - b*b
    sc = sN = sD = D
    tc = tN = tD = D
    
    if (D < SMALL_NUM):
        sN = 0.0
        sD = 1.0
        tN = e
        tD = c
    else:
        sN = (b*e - c*d)
        tN = (a*e - b*d)
        if sN < 0.0:
            sN = 0.0
            tN = e
            tD = c
        elif sN > sD:
            sN = sD
            tN = e + b
            tD = c

    if tN < 0.0:
        tN = 0.0;
        if -d < 0.0:
            sN = 0.0
        elif -d > a:
            sN = sD;
        else:
            sN = -d;
            sD = a;
    elif tN > tD:
        tN = tD
        
        if (-d + b) < 0.0:
            sN = 0
        elif (-d + b) > a:
            sN = sD
        else:
            sN = (-d + b)
            sD = a
    
    sc = 0.0 if abs(sN) < SMALL_NUM else sN / sD
    tc = 0.0 if abs(tN) < SMALL_NUM else tN / tD
    
    dP = w + (sc * u) - (tc * v)
    
    return np.linalg.norm(dP)