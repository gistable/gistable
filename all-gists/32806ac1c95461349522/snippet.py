import colorsys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
%matplotlib inline

def alter(alist, col, factor=1.1):
    tmp = np.array(alist)
    tmp[:,col] = tmp[:,col] * factor
    tmp[tmp > 1] = 1
    tmp[tmp < 0] = 0
    
    new = []
    for row in tmp.tolist():
        new.append(tuple(row))
        
    return new
    

def rgb2hls(alist):
    alist = alist[:]
    for i, row in enumerate(alist):
        hls = colorsys.rgb_to_hls(row[0], row[1], row[2])
        alist[i] = hls
    return alist


def hls2rgb(alist):
    alist = alist[:]
    for i, row in enumerate(alist):
        hls = colorsys.hls_to_rgb(row[0], row[1], row[2])
        alist[i] = hls
    return alist


def lighten(alist, increase=0.2):
    factor = 1 + increase
    hls = rgb2hls(alist)
    new = alter(hls, 1, factor=factor)
    rgb = hls2rgb(new)
    return rgb


def darken(alist, decrease=0.2):
    factor = 1 - decrease
    hls = rgb2hls(alist)
    new = alter(hls, 1, factor=factor)
    rgb = hls2rgb(new)
    return rgb


def saturate(alist, increase=0.2):
    factor = 1 + increase
    hls = rgb2hls(alist)
    new = alter(hls, 2, factor=factor)
    rgb = hls2rgb(new)
    return rgb
    

def desaturate(alist, decrease=0.2):
    factor = 1 - decrease
    hls = rgb2hls(alist)
    new = alter(hls, 2, factor=factor)
    rgb = hls2rgb(new)
    return rgb

#Visual examples
copal = sns.color_palette("hls", 7)

sns.palplot(copal)
sns.palplot(lighten(copal))
sns.palplot(darken(copal))
sns.palplot(saturate(copal))
sns.palplot(desaturate(copal))