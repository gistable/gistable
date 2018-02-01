def nearby_spots_old(request, lat, lng, radius=5000, limit=50):
    """
    WITHOUT use of any external library, using raw MySQL and Haversine Formula
    http://en.wikipedia.org/wiki/Haversine_formula
    """
    radius = float(radius) / 1000.0

    query = """SELECT id, (6367*acos(cos(radians(%2f))
               *cos(radians(latitude))*cos(radians(longitude)-radians(%2f))
               +sin(radians(%2f))*sin(radians(latitude))))
               AS distance FROM demo_spot HAVING
               distance < %2f ORDER BY distance LIMIT 0, %d""" % (
        float(lat),
        float(lng),
        float(lat),
        radius,
        limit
    )

    queryset = Spot.objects.raw(query)
    serializer = SpotWithDistanceSerializer(queryset, many=True)

    return JSONResponse(serializer.data)


def nearby_spots_new(request, lat, lng, radius=5000, limit=50):
    """
    WITH USE OF GEODJANGO and POSTGIS
    https://docs.djangoproject.com/en/dev/ref/contrib/gis/db-api/#distance-queries
    """
    user_location = fromstr("POINT(%s %s)" % (lng, lat))
    desired_radius = {'m': radius}
    nearby_spots = Spot.objects.filter(
        mpoint__distance_lte=(user_location, D(**desired_radius))).distance(
        user_location).order_by('distance')[:limit]
    serializer = SpotWithDistanceSerializer(nearby_spots, many=True)

    return JSONResponse(serializer.data)
