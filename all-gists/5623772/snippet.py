from django.contrib.gis.measure import D

def nearby(point, radius, unit):
    """Lists the nearest points to `point`, includes the distance from the point.

    Sorted in ascending order (from closest to furthest point).

    - radius, the distance to limit the search
    - unit, can be kilometers or miles, etc.

    returns a QuerySet.

    See: https://docs.djangoproject.com/en/dev/ref/contrib/gis/geoquerysets/#distance
    """
    qs = MyModel.objects.all()
    qs = qs.filter(point__distance_lte=(point, D(**{unit: radius})))
    qs = qs.distance(point)  # at this point, the type of queryset is GeoQuerySet
    qs = qs.order_by('distance')
    return qs

nearest = nearby(Point(x, y), 5, 'km')
# => [point1, point2, ...., pointN]
print nearest[0].distance
# => '2392903 m'