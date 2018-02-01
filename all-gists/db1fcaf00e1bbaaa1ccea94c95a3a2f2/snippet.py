#
# Hi,
# this is the Python code I used to make the sea surface temperature anomaly
# visualization https://twitter.com/anttilip/status/899005930141921280.
# This is a version in which the AREA of the circle represents the temperature
# anomaly (not radius).
# The data is included in this file but I plan to write some kind of tutorial
# in the near future how the average temperatures were computed (using GDAL
# and suitable masks).
# Feel free to improve, modify, do whatever you want with this code. If you decide
# to use the code, make an improved version of it, or it is useful for you
# in some another way I would be happy to know about it. You can contact me
# for example in Twitter (@anttilip).
#
# Thanks and have fun!
# Antti
#
# To run this code and generate the video file:
# mkdir frames
# python oceanTemperatureAnomalies.py
# ffmpeg -framerate 28 -pattern_type glob -i 'frames/*.png' -c:v libx264 -pix_fmt yuv420p SeaSurfaceTemperatureAnomaliesArea.mp4
#
# ---------
#
# Copyright 2017 Antti Lipponen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from scipy.interpolate import interp1d

# data
tempdata = {
    'atlantic': np.array([-0.13032294, -0.02195676, -0.07490252, -0.16376209, -0.31066127,
                          -0.25776896, -0.10007707, -0.24946657, -0.35348863, -0.12380083,
                          -0.43061546, -0.27379604, -0.38139318, -0.36561797, -0.44075924,
                          -0.41273423, -0.30999954, -0.37593714, -0.44201238, -0.33599078,
                          -0.3833187, -0.37827356, -0.45242403, -0.67785822, -0.72777868,
                          -0.51180554, -0.42683943, -0.45324609, -0.53557396, -0.56704522,
                          -0.4438725, -0.56675714, -0.48552931, -0.4037825, -0.30415926,
                          -0.15020184, -0.31962242, -0.23230981, -0.36106422, -0.29599882,
                          -0.31913675, -0.22449283, -0.39822505, -0.38351061, -0.35068286,
                          -0.32853468, -0.23458637, -0.1733911, -0.3676732, -0.41046617,
                          -0.26128297, -0.21565295, -0.13858768, -0.10055252, -0.05391661,
                          -0.16308885, -0.17198808, 0.01833034, -0.07004477, -0.01491895,
                          0.13241263, 0.14416116, 0.03772822, -0.07291775, 0.2035535,
                          0.14719876, -0.2775209, -0.22188918, -0.14442428, -0.07939368,
                          -0.25390463, -0.07390924, 0.09123497, 0.06009239, -0.10525848,
                          -0.03783932, -0.16541783, -0.06235224, -0.03841429, -0.07409262,
                          -0.00455761, 0.02385426, 0.12402405, 0.01157161, -0.17287201,
                          -0.04979889, -0.01606432, -0.1678803, -0.10165317, 0.06394284,
                          -0.01910022, -0.09870318, 0.02799994, 0.24170378, -0.00892503,
                          0.03610956, -0.05259692, 0.09612476, 0.08065349, 0.18360105,
                          0.20852345, 0.1648043, 0.08712382, 0.17453432, 0.19238018,
                          0.12166844, 0.11581853, 0.33409794, 0.30592384, 0.31293662,
                          0.32040914, 0.17800133, -0.00420576, 0.20221109, 0.12537353,
                          0.29835661, 0.2175477, 0.2045858, 0.46283098, 0.34726118,
                          0.32110158, 0.37243874, 0.31288212, 0.46066964, 0.42474789,
                          0.49432112, 0.50236108, 0.39976138, 0.47531949, 0.49667808,
                          0.64787733, 0.48165828, 0.4507486, 0.45473516, 0.4695789,
                          0.49371041, 0.58652881]),
    'pacific': np.array([-0.0366684, 0.05529764, 0.09838816, 0.0151098, -0.01333696,
                         -0.17042, -0.31948081, -0.23137482, 0.13234657, -0.01652401,
                         -0.24327535, -0.02177389, -0.12921416, -0.21381572, -0.22812433,
                         -0.007107, 0.15295377, 0.06295084, -0.1130817, -0.00098956,
                         0.07846443, 0.0304071, -0.10702398, -0.32388295, -0.39498111,
                         -0.09964156, -0.15952832, -0.22608949, -0.46245491, -0.55354938,
                         -0.55106763, -0.46773799, -0.26839208, -0.34140643, -0.19876606,
                         -0.17116869, -0.41464227, -0.53476796, -0.13391002, -0.28757963,
                         -0.265931, -0.27066805, -0.29142747, -0.23050584, -0.28117498,
                         -0.18335062, -0.0850034, -0.21636735, -0.24528013, -0.21263072,
                         -0.12433348, -0.10925778, -0.24677262, -0.3821907, -0.31690365,
                         -0.25223774, -0.25759468, -0.14513574, -0.28499956, -0.0970738,
                         0.18728452, 0.26401316, 0.02182967, 0.15739666, 0.20076484,
                         0.22189142, -0.05942365, -0.02164623, -0.19008755, -0.1617324,
                         -0.15910169, -0.00506088, 0.06030459, 0.02348508, -0.20694627,
                         -0.28868397, -0.10271197, 0.17874435, 0.12688624, 0.03385398,
                         0.04507188, -0.00355556, -0.05562074, 0.12765102, -0.11448988,
                         -0.02754484, -0.03785693, -0.01470264, 0.06163825, 0.21358111,
                         -0.00106855, -0.20682404, 0.10102283, -0.02354255, -0.12561375,
                         -0.24694516, -0.08479319, 0.11106477, 0.01329984, 0.20952735,
                         0.23982977, 0.16165056, 0.23375304, 0.21918976, 0.13809988,
                         0.02861324, 0.16574068, 0.25630929, 0.14287106, 0.1291562,
                         0.30478007, 0.33618753, 0.28198483, 0.19731928, 0.29576043,
                         0.26934926, 0.24674876, 0.49576764, 0.3233111, 0.05220987,
                         0.14745642, 0.33227278, 0.43163974, 0.40829386, 0.46126388,
                         0.40904834, 0.38261141, 0.22108537, 0.22143657, 0.44277001,
                         0.24267018, 0.16678782, 0.29073417, 0.37762869, 0.53308235,
                         0.72210354, 0.69073493]),
    'indian': np.array([-0.14435229, -0.05486208, -0.12947393, -0.11577365, -0.21573373,
                        -0.26125068, -0.17651342, -0.2953353, -0.06041497, -0.10293487,
                        -0.3551261, -0.16907735, -0.07479699, -0.17196385, -0.12252529,
                        -0.13576235, 0.00674022, -0.01320466, -0.29990999, -0.3696527,
                        -0.11194672, -0.36807528, -0.30017169, -0.35006769, -0.51751909,
                        -0.37381017, -0.28009257, -0.32372333, -0.42718369, -0.41587013,
                        -0.42587552, -0.38630381, -0.1750004, -0.31272384, -0.08385214,
                        -0.07222764, -0.25033035, -0.2382717, -0.16720962, -0.14742339,
                        -0.17781167, -0.20560479, -0.24054681, -0.31994464, -0.35166865,
                        -0.30312195, -0.26412727, -0.37098285, -0.32283552, -0.4620912,
                        -0.28110051, -0.19236609, -0.3431981, -0.285866, -0.21804161,
                        -0.27941352, -0.09931221, -0.12773262, -0.10857717, -0.16042625,
                        0.08853802, 0.41177935, 0.13675998, -0.06034624, 0.31728147,
                        0.1893879, -0.05934331, -0.25549241, -0.13365288, -0.07082778,
                        -0.05397824, -0.15296481, -0.13281408, -0.06836453, -0.19907482,
                        -0.20842138, -0.22532048, -0.07612384, 0.02888666, 0.02844808,
                        -0.15446249, 0.03994097, 0.05098855, -0.10775422, -0.17833652,
                        -0.22550834, -0.09645969, -0.01101758, -0.18314302, 0.12377716,
                        0.10408222, 0.00434557, 0.14483923, 0.1359361, -0.02607415,
                        0.03364314, 0.16337757, 0.34005145, 0.2411591, 0.31467977,
                        0.29168452, 0.27177424, 0.29176438, 0.48758311, 0.23902758,
                        0.34405435, 0.27456427, 0.5342205, 0.51494181, 0.31234629,
                        0.39864483, 0.42536825, 0.3534947, 0.32551905, 0.26587778,
                        0.29495444, 0.33264077, 0.43581219, 0.55115536, 0.37893177,
                        0.37783927, 0.46863074, 0.50250673, 0.47453909, 0.40624299,
                        0.3657718, 0.41274371, 0.48429514, 0.40230859, 0.52891874,
                        0.6690956, 0.62820143, 0.6230634, 0.57288792, 0.63788997,
                        0.80972338, 0.70668441])
}
time = np.arange(1880.5, 2017.0)

# list of colors
fontName = 'Lato'
backgroundColor = '#faf2eb'
titleColor = '#2a4957'
textColor = '#807f82'
lineColor = '#384d58'
oceanNameColor = '#188391'

# matplotlib params
plt.rcParams['axes.facecolor'] = backgroundColor
mpl.rcParams.update({'font.size': 22})

# colormap & norms
cmapTcolor = plt.get_cmap('RdYlBu_r')
normTcolor = mpl.colors.Normalize(vmin=-0.75, vmax=0.75)
normTradius = mpl.colors.Normalize(vmin=-1.0, vmax=1.0)


# get time function
def getTime(xx):
    mintime, maxtime = 1880.0, 2018.5
    clipmax = 2016.5
    clipmin = 1880.5
    return np.clip(((np.tanh(xx * 2.5 - 0.5) + 0.45) / 1.4) * (maxtime - mintime) + mintime, a_min=clipmin, a_max=clipmax)


# temperaturedata interpolators
atlanticTintp = interp1d(time, tempdata['atlantic'])
pacificTintp = interp1d(time, tempdata['pacific'])
indianTintp = interp1d(time, tempdata['indian'])

zeroradius = np.sqrt((0.5 * (np.pi * 1.0**2 + np.pi * 0.2**2)) / np.pi)  # radius corresponding to anomaly 0.0 (-1.0 = radius 0.2, +1.0 = radius 1.0)
Nframes = 925  # N of frames
for ii in range(Nframes):

    # ok, just use 860 frames here...
    if ii >= 860:
        continue

    # get time
    t = getTime(ii / Nframes)
    year = np.floor(t)
    print(t)

    # compute circle radius
    indianT = indianTintp(t)
    indianArea = np.pi * 0.2**2 + (np.pi * 1.0**2 - np.pi * 0.2**2) * normTradius(indianT)
    indianR = np.sqrt(indianArea / np.pi)
    atlanticT = atlanticTintp(t)
    atlanticArea = np.pi * 0.2**2 + (np.pi * 1.0**2 - np.pi * 0.2**2) * normTradius(atlanticT)
    atlanticR = np.sqrt(atlanticArea / np.pi)
    pacificT = pacificTintp(t)
    pacificArea = np.pi * 0.2**2 + (np.pi * 1.0**2 - np.pi * 0.2**2) * normTradius(pacificT)
    pacificR = np.sqrt(pacificArea / np.pi)

    # get time series data
    fullT = np.linspace(1880.5, 2016.5, 1000)
    indianTStime = (fullT[fullT <= t] - 1880.5) / (2016.5 - 1880.5) * 2.4 - 1.2
    indianTStemp = indianTintp(fullT[fullT <= t]) / 0.75 * 0.5
    atlanticTStime = (fullT[fullT <= t] - 1880.5) / (2016.5 - 1880.5) * 2.4 - 1.2
    atlanticTStemp = atlanticTintp(fullT[fullT <= t]) / 0.75 * 0.5
    pacificTStime = (fullT[fullT <= t] - 1880.5) / (2016.5 - 1880.5) * 2.4 - 1.2
    pacificTStemp = pacificTintp(fullT[fullT <= t]) / 0.75 * 0.5

    # construct figure
    fig, ax = plt.subplots(figsize=(12, 6))
    renderer = fig.canvas.get_renderer()
    transf = ax.transData.inverted()

    c = Circle((-2.5, 0.0), radius=0.2, fill=False, linestyle='--', linewidth=0.2, color=lineColor, zorder=10)
    ax.add_patch(c)
    c = Circle((-2.5, 0.0), radius=zeroradius, fill=False, linestyle='--', linewidth=0.4, color=lineColor, zorder=10)
    ax.add_patch(c)
    c = Circle((-2.5, 0.0), radius=1.0, fill=False, linestyle='--', linewidth=0.2, color=lineColor, zorder=10)
    ax.add_patch(c)
    c = Circle((-2.5, 0.0), radius=pacificR, fill=True, color=cmapTcolor(normTcolor(pacificT)), zorder=50, alpha=0.5)
    ax.add_patch(c)
    c = Circle((-2.5, 0.0), radius=pacificR, fill=False, linewidth=1.0, color='k', zorder=51, alpha=1.0)
    ax.add_patch(c)
    c = Circle((-2.5, pacificR), radius=0.01, fill=False, linewidth=1.85, color='k', zorder=51, alpha=1.0)
    ax.add_patch(c)
    plt.text(
        -2.5,
        1.4,
        'Pacific Ocean',
        {'ha': 'center', 'va': 'center'},
        fontsize=17,
        fontname=fontName,
        color=oceanNameColor,
        clip_on=False
    )
    offset = -2.5
    ax.plot(pacificTStime + offset, pacificTStemp - 1.65, linewidth=0.5, linestyle='-', color=lineColor, clip_on=False)
    ax.plot([offset - 1.2, offset + 1.2], [-1.65, -1.65], linewidth=0.25, linestyle='-', color=lineColor, clip_on=False)
    f = interp1d([1880.5, 2016.5], [offset - 1.2, offset + 1.2])
    for jj in [f(1880.5), f(1900.5), f(1920.5), f(1940.5), f(1960.5), f(1980.5), f(2000.5)]:  # parilliset vuosikymmenet
        ax.plot([jj, jj], [-1.62, -1.68], linewidth=0.25, linestyle='-', color=lineColor, clip_on=False)
    for jj in [f(1890.5), f(1910.5), f(1930.5), f(1950.5), f(1970.5), f(1990.5), f(2010.5)]:  # parittomat vuosikymmenet
        ax.plot([jj, jj], [-1.64, -1.66], linewidth=0.25, linestyle='-', color=lineColor, clip_on=False)

    c = Circle((0.0, 0.0), radius=0.2, fill=False, linestyle='--', linewidth=0.2, color=lineColor, zorder=10)
    ax.add_patch(c)
    c = Circle((0.0, 0.0), radius=zeroradius, fill=False, linestyle='--', linewidth=0.4, color=lineColor, zorder=10)
    ax.add_patch(c)
    c = Circle((0.0, 0.0), radius=1.0, fill=False, linestyle='--', linewidth=0.2, color=lineColor, zorder=10)
    ax.add_patch(c)
    c = Circle((0.0, 0.0), radius=atlanticR, fill=True, color=cmapTcolor(normTcolor(atlanticT)), zorder=50, alpha=0.5)
    ax.add_patch(c)
    c = Circle((0.0, 0.0), radius=atlanticR, fill=False, linewidth=1.0, color='k', zorder=51, alpha=1.0)
    ax.add_patch(c)
    c = Circle((0.0, atlanticR), radius=0.01, fill=False, linewidth=1.85, color='k', zorder=51, alpha=1.0)
    ax.add_patch(c)
    plt.text(
        0.0,
        1.4,
        'Atlantic Ocean',
        {'ha': 'center', 'va': 'center'},
        fontsize=17,
        fontname=fontName,
        color=oceanNameColor,
        clip_on=False
    )
    offset = 0.0
    ax.plot(atlanticTStime + offset, atlanticTStemp - 1.65, linewidth=0.5, linestyle='-', color=lineColor, clip_on=False)
    ax.plot([offset - 1.2, offset + 1.2], [-1.65, -1.65], linewidth=0.25, linestyle='-', color=lineColor, clip_on=False)
    f = interp1d([1880.5, 2016.5], [offset - 1.2, offset + 1.2])
    for jj in [f(1880.5), f(1900.5), f(1920.5), f(1940.5), f(1960.5), f(1980.5), f(2000.5)]:  # parilliset vuosikymmenet
        ax.plot([jj, jj], [-1.62, -1.68], linewidth=0.25, linestyle='-', color=lineColor, clip_on=False)
    for jj in [f(1890.5), f(1910.5), f(1930.5), f(1950.5), f(1970.5), f(1990.5), f(2010.5)]:  # parittomat vuosikymmenet
        ax.plot([jj, jj], [-1.64, -1.66], linewidth=0.25, linestyle='-', color=lineColor, clip_on=False)

    c = Circle((2.5, 0.0), radius=0.2, fill=False, linestyle='--', linewidth=0.2, color=lineColor, zorder=10)
    ax.add_patch(c)
    c = Circle((2.5, 0.0), radius=zeroradius, fill=False, linestyle='--', linewidth=0.4, color=lineColor, zorder=10)
    ax.add_patch(c)
    c = Circle((2.5, 0.0), radius=1.0, fill=False, linestyle='--', linewidth=0.2, color=lineColor, zorder=10)
    ax.add_patch(c)
    c = Circle((2.5, 0.0), radius=indianR, fill=True, color=cmapTcolor(normTcolor(indianT)), zorder=50, alpha=0.5)
    ax.add_patch(c)
    c = Circle((2.5, 0.0), radius=indianR, fill=False, linewidth=1.0, color='k', zorder=51, alpha=1.0)
    ax.add_patch(c)
    c = Circle((2.5, indianR), radius=0.01, fill=False, linewidth=1.85, color='k', zorder=51, alpha=1.0)
    ax.add_patch(c)
    plt.text(
        2.5,
        1.4,
        'Indian Ocean',
        {'ha': 'center', 'va': 'center'},
        fontsize=17,
        fontname=fontName,
        color=oceanNameColor,
        clip_on=False
    )
    offset = 2.5
    ax.plot(indianTStime + offset, indianTStemp - 1.65, linewidth=0.5, linestyle='-', color=lineColor, clip_on=False)
    ax.plot([offset - 1.2, offset + 1.2], [-1.65, -1.65], linewidth=0.25, linestyle='-', color=lineColor, clip_on=False)
    f = interp1d([1880.5, 2016.5], [offset - 1.2, offset + 1.2])
    for jj in [f(1880.5), f(1900.5), f(1920.5), f(1940.5), f(1960.5), f(1980.5), f(2000.5)]:  # parilliset vuosikymmenet
        ax.plot([jj, jj], [-1.62, -1.68], linewidth=0.25, linestyle='-', color=lineColor, clip_on=False)
    for jj in [f(1890.5), f(1910.5), f(1930.5), f(1950.5), f(1970.5), f(1990.5), f(2010.5)]:  # parittomat vuosikymmenet
        ax.plot([jj, jj], [-1.64, -1.66], linewidth=0.25, linestyle='-', color=lineColor, clip_on=False)

    plt.text(
        -3.95,
        -1.65,
        '0.0 $^\circ$C',
        {'ha': 'right', 'va': 'center'},
        fontsize=8,
        fontname=fontName,
        clip_on=False
    )

    rs = [[0.2, '-1.0 $^\circ$C'], [zeroradius, '0.0 $^\circ$C'], [1.0, '+1.0 $^\circ$C']]
    for r in rs:
        ax.plot([-3.9, -2.5],
                [r[0], r[0]],
                linewidth=0.25, linestyle='--', color=lineColor, zorder=11, clip_on=False)
        plt.text(
            -3.95,
            r[0],
            r[1],
            {'ha': 'right', 'va': 'center'},
            fontsize=10,
            fontname=fontName,
            clip_on=False
        )

    plt.text(
        -4.8 + 0.005,
        1.95 - 0.005,
        'Sea Surface Temperature Anomalies',
        {'ha': 'left', 'va': 'center'},
        fontsize=20,
        fontname=fontName,
        color='k',
        clip_on=False
    )
    plt.text(
        -4.8,
        1.95,
        'Sea Surface Temperature Anomalies',
        {'ha': 'left', 'va': 'center'},
        fontsize=20,
        fontname=fontName,
        color=titleColor,
        clip_on=False
    )

    plt.text(
        4.27 - 0.3,
        1.9,
        str(int(year)),
        {'ha': 'center', 'va': 'center'},
        fontsize=24,
        fontname=fontName,
        color=titleColor,
        clip_on=False
    )

    plt.text(
        -4.8,
        -1.4 - 0.8,
        'Data source: Extended Reconstructed Sea Surface Temperature (ERSST) v5',
        {'ha': 'left', 'va': 'center'},
        fontsize=10,
        fontname=fontName,
        color='#888888',
        clip_on=False
    )
    plt.text(
        -4.8,
        -1.55 - 0.8,
        'https://www.ncdc.noaa.gov/data-access/marineocean-data/',
        {'ha': 'left', 'va': 'center'},
        fontsize=10,
        fontname=fontName,
        color='#888888',
        clip_on=False
    )
    plt.text(
        -4.8,
        -1.7 - 0.8,
        'Base period: 1951–1980, average of monthly temperature anomalies',
        {'ha': 'left', 'va': 'center'},
        fontsize=10,
        fontname=fontName,
        color='#888888',
        clip_on=False
    )
    plt.text(
        4.3 + 0.2,
        -1.55 - 0.8,
        'Antti Lipponen (@anttilip)',
        {'ha': 'right', 'va': 'center'},
        fontsize=9,
        fontname=fontName,
        color='#888888',
        clip_on=False
    )
    plt.text(
        4.3 + 0.2,
        -1.7 - 0.8,
        'License: CC BY 4.0',
        {'ha': 'right', 'va': 'center'},
        fontsize=9,
        fontname=fontName,
        color='#888888',
        clip_on=False
    )
    ax.set_xlim([-3.8, 3.8])
    ax.set_ylim([-2.1, 1.65])
    plt.axis('off')
    plt.savefig('frames/animframes_{:04d}.png'.format(ii + 1), facecolor=backgroundColor, edgecolor='none', dpi=150)
    plt.close()

    # Data: Extended Reconstructed Sea Surface Temperature (ERSST) v5.
    # https://www.ncdc.noaa.gov/data-access/marineocean-data/
    # Base period: 1971–2000, average of monthly temperature anomalies
    # Antti Lipponen (@anttilip)
    # License: CC BY 4.0
