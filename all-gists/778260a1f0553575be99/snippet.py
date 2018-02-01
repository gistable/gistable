# Resulting video from this code can be seen here:
#   http://www.ifweassume.com/2015/02/world-population-density.html
# or
#   https://vimeo.com/120308257

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import os

file = 'gl_gpwv3_pcount_00_ascii_25/glp00g.asc'
pop_data = np.loadtxt(file, skiprows=6)
# data file from here:
# http://sedac.ciesin.columbia.edu/data/set/gpw-v3-population-density/data-download

xo = np.arange(-180,180,0.0416666666667)
yo = np.arange(-58,85,0.0416666666667)
xx,yy = np.meshgrid(xo,yo,indexing='xy')

i=0
# go from positive to negative, make globe spin correctly
for lon in xrange(180,-180,-1):
    print(i+1, ' ', lon)
    map = Basemap(projection='ortho', lat_0=10, lon_0=lon, resolution='l')
    xm, ym = map(xx,yy)

    plt.figure(figsize=(9,9))
    map.contourf(xm, ym, np.log10(pop_data[::-1, :] +1), cmap=plt.cm.Blues)
    map.drawcoastlines(linewidth=1.25)
    map.drawparallels(np.arange(-90.,91.,30.))
    map.drawmeridians(np.arange(-180, 181., 60.))

    plt.savefig("img/frame" + format(i, '04') + '.jpeg')
    plt.clf()
    plt.close()
    i = i+1
    
# render the video file using FFMPEG
os.system('ffmpeg -r 20 -i img/frame%04d.jpeg -qscale 1 movie.mp4')