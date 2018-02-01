#!/env/python
# coding=utf8

"""
Converting Degrees, Minutes, Seconds formatted coordinate strings to decimal. 

Formula:
DEC = (DEG + (MIN * 1/60) + (SEC * 1/60 * 1/60))

Assumes S/W are negative. 
"""

import re

def dms2dec(dms_str):
    """Return decimal representation of DMS
    
    >>> dms2dec(utf8(48°53'10.18"N))
    48.8866111111F
    
    >>> dms2dec(utf8(2°20'35.09"E))
    2.34330555556F
    
    >>> dms2dec(utf8(48°53'10.18"S))
    -48.8866111111F
    
    >>> dms2dec(utf8(2°20'35.09"W))
    -2.34330555556F
    
    """
    
    dms_str = re.sub(r'\s', '', dms_str)
    
    if re.match('[swSW]', dms_str):
        sign = -1
    else:
        sign = 1
    
    (degree, minute, second, frac_seconds, junk) = re.split('\D+', dms_str, maxsplit=4)
    
    return sign * (int(degree) + float(minute) / 60 + float(second) / 3600 + float(frac_seconds) / 36000)