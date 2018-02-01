#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Modified from:  http://stackoverflow.com/questions/14114610/finding-centre-of-a-polygon-using-limited-data
See also: http://en.wikipedia.org/wiki/Centroid#Centroid_of_polygon

NOTE: All the following geolocations calculations assumed that
the distance from each position is short, i.e. that can be considered to over a flat surface.
Otherwise, converting to spherical coordinates needs to be implemented.
"""
__license__ = "GPL-3.0"
 
import itertools as IT
 
def area_of_polygon(x, y):
    """Calculates the signed area of an arbitrary polygon given its verticies
    http://stackoverflow.com/a/4682656/190597 (Joe Kington)
    http://softsurfer.com/Archive/algorithm_0101/algorithm_0101.htm#2D%20Polygons
    """
    area = 0.0
    for i in xrange(-1, len(x) - 1):
        area += x[i] * (y[i + 1] - y[i - 1])
    return area / 2.0
 
def centroid_of_polygon(points):
    """
    http://stackoverflow.com/a/14115494/190597 (mgamba)
    """
    area = area_of_polygon(*zip(*points))
    result_x = 0
    result_y = 0
    N = len(points)
    points = IT.cycle(points)
    x1, y1 = next(points)
    for i in range(N):
        x0, y0 = x1, y1
        x1, y1 = next(points)
        cross = (x0 * y1) - (x1 * y0)
        result_x += (x0 + x1) * cross
        result_y += (y0 + y1) * cross
    result_x /= (area * 6.0)
    result_y /= (area * 6.0)
    return (result_x, result_y)
 
def midpoint(points):
    # returning the array as tuple
    return tuple(np.mean(points, axis=0).tolist())
 
def calculate_centroid(site_location):
    # (159.2903828197946, 98.88888888888889)
    cent = {}
    for site in site_location.keys():
        points = site_location[site]["locations"]
        if len(points) == 2:
            cent[site] = {"centroid":midpoint(points),"metadata":"using midpoint location"}
        if len(points) == 1:
            cent[site] = {"centroid":points[0],"metadata":"unique location point"}
        if len(points) > 2:
            cent[site] = {"centroid": centroid_of_polygon(points), "metadata":"centroid of gift-wraping polygon"}
    return cent
 
# Example of its use by using a python dictionary
site_location = dict({"B1":{}})
site_location["B1"] = {'locations': [(17.624283333299999, 58.802750000000003),
  (17.624779999999998, 58.802259999999997),
  (17.62472, 58.802430000000008),
  (17.625520000000002, 58.802349999999997),
  (17.62538, 58.80265)]}
 
harmonized_site_locations = calculate_centroid(site_location)