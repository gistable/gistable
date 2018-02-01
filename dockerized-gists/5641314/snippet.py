"""A simple GeoPoint object to generate random points nearby."""

import math
import random


class GeoPoint(object):

    """Represents a geolocation point with latitude and longitude."""

    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'GeoPoint(lat: {}, lng: {})'.format(self.lat, self.lng)

    def random_nearby_points(self, radius=1000, count=1):
        """Generate number of random points in a radius.

        Args:
          radius: Maximum distance from the point.
          count: Number of points to generate.
        Returns:
          List of GeoPoint objects.
        """
        points = []
        for i in xrange(count):
            points.append(self.random_nearby_point(radius))
        return points

    def random_nearby_point(self, radius=1000):
        """Generate a random point in a radius.

        Reference URL: http://goo.gl/KWcPE.

        Args:
          radius: Maximum distance from the point.
        Returns:
          GeoPoint object.
        """
        # Convert Radius from meters to degrees.
        rd = radius / 111300.0

        u = random.random()
        v = random.random()

        w = rd * math.sqrt(u)
        t = 2.0 * math.pi * v
        x = w * math.cos(t)
        y = w * math.sin(t)

        xp = x / math.cos(self.lat) / 1.0

        return GeoPoint(y + self.lat, xp + self.lng)
