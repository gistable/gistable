#! /usr/bin/env python

import scipy.io as sio
import matplotlib.pyplot as plt

class BadSeriesError(Exception): pass

class MatRwl(object):
    """ Read MATLAB files from Meko's RWL Velmex script.
    """
    # self._series["series_id"][:,0] gives years.
    # self._series["series_id"][:,1] gives measurements.
    def __init__(self, fl):
       d_raw = sio.loadmat(fl)
       self._series = dict()
       series_id = d_raw["XT"]["id"][0][0][0]
       series_data = d_raw["XT"]["data"][0][0][0]
       if len(series_id) != len(series_data):
           raise BadSeriesError, "Series names and series data have different lengths"
       for i in xrange(len(d_id)):
           self._series[series_id[i][0]] = series_data[i]

    def getSeries(self, series_name):
        """ Return a numpy array with values and observation year for a series.
        """
        return(self._series[series_name])

    def getSeriesYears(self, series_name):
        """ Return array of observation years for a named ring-width series.
        """
        return(self._series[series_name][:, 0])

    def getSeriesValues(self, series_name):
        """ Return array of measurement values for a named ring-width series.
        """
        return(self._series[series_name][:, 1])
    
    def getSeriesYearRange(self, series_name):
        """ Return (min_year, max_year) for a given ring-width series.
        """
        return((min(self.getSeriesYears(series_name)),
            max(self.getSeriesYears(series_name))))

    def getSeriesIds(self):
        """ Return a list of unicode string series names.
        """
        return(self._series.keys())
    
    def plotSeries(self, series_name):
        y = self.getSeriesValues(series_name)
        x = self.getSeriesYears(series_name)
        plt.plot(x, y, "k")
        plt.ylabel("Ring-width index")
        plt.xlabel("Year")
        plt.show()
