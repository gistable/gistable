# -*- coding: utf-8 -*-
import math

def calculate_orthodromic_distance(pointA, pointB):
    """
    Calculates the great circle distance between two points.
    The great circle distance is the shortest distance.
    This function uses the Haversine formula :
      - https://en.wikipedia.org/wiki/Haversine_formula

    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees

    :Returns:
      The distance in nautical miles (N)

    :Returns Type:
      float
    """
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    earth_radius = 6371 # Kms
    nautical_mile = 1.852

    diffLat  = math.radians(pointB[0] - pointA[0])
    diffLong = math.radians(pointB[1] - pointA[1])

    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    a = math.sin(diffLat / 2) * math.sin(diffLat / 2) +   \
        math.sin(diffLong / 2) * math.sin(diffLong / 2) * \
        math.cos(lat1) * math.cos(lat2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = (earth_radius * c) / nautical_mile

    if math.modf(distance)[0] >= 0.5:
        distance = math.ceil(distance)
    else:
        distance = math.floor(distance)

    return int(distance)
