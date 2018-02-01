import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import NullFormatter

# based on http://www.astrobetter.com/blog/2014/02/10/visualization-fun-with-python-2d-histogram-with-1d-histograms-on-axes/
def fancy_2d_plot(xvals, yvals):
    '''makes a histogran with sidecars:
    2D histogram shown as an image in center, with
    1D histograms corresponding to the 2 axes along each side

    input: xvals, yvals: X and Y positions of points to be histogrammed
    '''

    hist_2d_all, xedge, yedge = np.histogram2d(xvals, yvals, bins=8)

    # start with a rectangular Figure
    f = plt.figure(figsize=(8,8))
    
    # define where the axes go
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left+width+0.02
    
    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.2]
    rect_histy = [left_h, bottom, 0.15, height]
    
    # add the axes to the figure
    ax2d = plt.axes(rect_scatter)
    axHistx = plt.axes(rect_histx)
    axHisty = plt.axes(rect_histy)
    
    # no labels for the sidecar histograms, because the 2D plot has them
    nullfmt   = NullFormatter()         
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)
    
    # the 2D plot:
    # note the all-important transpose!
    plot2d = ax2d.imshow(hist2d.T, interpolation='none', origin='low',\
      extent=[xedge[0], xedge[-1], yedge[0], yedge[-1]],aspect='auto',cmap=cm.coolwarm)
    ax2d.set_xlabel('Input magnitude')
    ax2d.set_ylabel('Galactocentric distance [arcmin]')
    plt.colorbar(plot2d)
    
    # the 1-D histograms: first the X-histogram
    xhist = hist2d.sum(axis=1) # note x-hist is axis 1, not 0
    axHistx.bar(left=xedge[:-1], height=xhist, width = xedge[1:]-xedge[:-1])
    axHistx.set_xlim( ax2d.get_xlim()) # x-limits match the 2D plot
    axHistx.set_ylabel('Detection fraction')
    axHistx.set_yticks([0.1, 0.4, 0.7, 1.0])

    # then the Y-histogram
    yhist = hist2d.sum(axis=0) # note y-hist is axis 0, not 1
    # use barh instead of bar here because we want a horizontal histogram
    axHisty.barh(bottom=yedge[:-1], width=yhist, height = yedge[1:]-yedge[:-1])
    axHisty.set_ylim( ax2d.get_ylim()) # y-limits match the 2D plot
    axHisty.set_xlim(0,0.8)
    axHisty.set_xlabel('Detection fraction')
    axHisty.set_xticks([0.2, 0.5, 0.8])
        
    plt.show()
    return

