"""
Shows how to do a cross join (i.e. cartesian product) between two pandas DataFrames using an example on
calculating the distances between origin and destination cities.

Tested with pandas 0.17.1 and 0.18 on Python 3.4 and Python 3.5

Best run this with Spyder (see https://github.com/spyder-ide/spyder)
Author: Markus Konrad <post@mkonrad.net>

April 2016
"""

import pandas as pd
import math

#%% define some functions that we'll need

def df_crossjoin(df1, df2, **kwargs):
    """
    Make a cross join (cartesian product) between two dataframes by using a constant temporary key.
    Also sets a MultiIndex which is the cartesian product of the indices of the input dataframes.
    See: https://github.com/pydata/pandas/issues/5401
    :param df1 dataframe 1
    :param df1 dataframe 2
    :param kwargs keyword arguments that will be passed to pd.merge()
    :return cross join of df1 and df2
    """
    df1['_tmpkey'] = 1
    df2['_tmpkey'] = 1

    res = pd.merge(df1, df2, on='_tmpkey', **kwargs).drop('_tmpkey', axis=1)
    res.index = pd.MultiIndex.from_product((df1.index, df2.index))

    df1.drop('_tmpkey', axis=1, inplace=True)
    df2.drop('_tmpkey', axis=1, inplace=True)

    return res


def haversine(p1, p2):
    """
    Calculate distance between two points on earth in km
    See: http://www.movable-type.co.uk/scripts/latlong.html
    :param p1 point 1 tuple (latitude, longitude)
    :param p2 point 2 tuple (latitude, longitude)
    :return distance between points p1 and p2 on earth in km
    """
    R = 6371     # earth radius in km
    p1 = [math.radians(v) for v in p1]
    p2 = [math.radians(v) for v in p2]

    d_lat = p2[0] - p1[0]
    d_lng = p2[1] - p1[1]
    a = math.pow(math.sin(d_lat / 2), 2) + math.cos(p1[0]) * math.cos(p2[0]) * math.pow(math.sin(d_lng / 2), 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


#%% define the data

origin_cities = ['Berlin',  'Hamburg', 'Munich']
origin_coords = {
    'lat':  [52.518611, 53.550556, 48.137222],
    'lng':  [13.408333, 9.993333,  11.575556]
}

destination_cities = ['London',  'New York City', 'Moscow', 'Sydney', 'Istanbul']
destination_coords = {
    'lat':  [51.50939,  40.712778, 55.75,    -33.85, 41.01],
    'lng':  [-0.11832, -74.005833, 37.616667, 151.2, 28.960278]
}

df_orig = pd.DataFrame(origin_coords, index=origin_cities)
df_dest = pd.DataFrame(destination_coords, index=destination_cities)

print(df_orig)
print(df_dest)

#%% perform the cross join

dfx = df_crossjoin(df_orig, df_dest, suffixes=('_orig', '_dest'))

print(dfx)

#%% calculate the distances by applying the haversine() function to each row

dist = dfx.apply(lambda row: haversine((row['lat_orig'], row['lng_orig']), (row['lat_dest'], row['lng_dest'])),
                 axis=1)
print(dist)

#%% get the 3 smallest distances per origin city
nearest3 = dist.groupby(level=0).nsmallest(3)
print(nearest3)