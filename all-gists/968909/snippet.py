'''
Created on 2011-05-12

@author: Daniel Sokolowski

Extends django's built in JSON serializer to support GEOJSON encoding

Requirements:
    Install and setup geodjango (django.contrib.gis)

Install:
    Add ``SERIALIZATION_MODULES = { 'geojson' : 'path.to.geojson_serializer' }`` to your 
    project ``settings.py`` file.
    
Usage:
    from django.core import serializers
    geojson = serializers.serialize("geojson", <Model>.objects.all())

'''
from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers.json import Serializer as OverloadedSerializer
from django.utils import simplejson
from django.contrib.gis.db.models.fields import GeometryField
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.utils import simplejson as json


class Serializer(OverloadedSerializer):
    def handle_field(self, obj, field):
        """
        If field is of GeometryField than encode otherwise call parent's method
        """
        value = field._get_val_from_obj(obj)
        if isinstance(field, GeometryField):
            self._current[field.name] = value
        else:
            super(Serializer, self).handle_field(obj, field)

    
    def end_serialization(self):
        simplejson.dump(self.objects, self.stream, cls=DjangoGEOJSONEncoder, **self.options)

class DjangoGEOJSONEncoder(DjangoJSONEncoder):
    """
    DjangoGEOJSONEncoder subclass that knows how to encode GEOSGeometry value
    """
    
    def default(self, o):
        """ overload the default method to process any GEOSGeometry objects otherwise call original method """ 
        print(type(o))
        if isinstance(o, GEOSGeometry):
            return json.loads(o.geojson)
        else:
            super(DjangoGEOJSONEncoder, self).default(o)


