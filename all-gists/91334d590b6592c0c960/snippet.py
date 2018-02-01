import datetime
import six

from django.contrib.gis.geos import Point, MultiPoint

from haystack import indexes
from haystack.exceptions import SpatialError, SearchFieldError
from haystack.utils.geo import ensure_geometry, ensure_point

def ensure_multipoint(geom):
    """
    Makes sure the parameter passed in looks like a GEOS ``MultiPoint``.
    """
    ensure_geometry(geom)

    if geom.geom_type != 'MultiPoint':
        raise SpatialError("Provided geometry '%s' is not a 'MultiPoint'." % geom)

    return geom


class MultiLocationField(indexes.SearchField):
    '''
    A field for specifying multiple locations for a single document.
    Spatial queries will include the document if any of the points in 
    the MultiPointField match the query.
    
    Input can be a MultiPoint GEOS geometry object, an array of Point GEOS geometry objects,
    or a sequence of any representation of a Point object recognized by the built-in LocationField
    ((lat,long) tuples, {"lat": lat, "long": long} dictionary, or "lat,long" string.)
    
    Works with elasticsearch backend for sure. Haven't tested with other backends.
    '''
    field_type = 'location'

    def __init__(self, **kwargs):
    
        super(MultiLocationField, self).__init__(**kwargs)
        self.is_multivalued = True

    def prepare(self, obj):

        value = super(MultiPointField, self).prepare(obj)

        if value is None:
            return None

        return ['{0},{1}'.format(point.y, point.x) for point in value]

    def convert(self, value):

        if value is None:
            return None

        if hasattr(value, 'geom_type'):
            value = ensure_multipoint(value)
            value = [Point(coord[0], coord[1]) for coord in value.coords]
            return value

        for point in value:

            # Essentially copied from LocatonField. Probably not the DRYest code
            if hasattr(point, 'geom_type'):
                point = ensure_point(value)
                continue

            if isinstance(point, six.string_types):
                lat, lng = point.split(',')
            elif isinstance(point, (list, tuple)):
                # GeoJSON-alike
                lat, lng = point[1], point[0]
            elif isinstance(point, dict):
                lat = point.get('lat', 0)
                lng = point.get('lon', 0)

            point = Point(float(lng), float(lat))

        return value