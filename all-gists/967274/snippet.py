try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import datetime
import decimal

from django.core.serializers.python import Serializer as PythonSerializer
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import is_protected_type, smart_unicode
from django.utils import simplejson as json
from django.utils import datetime_safe
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.contrib.gis.db.models.fields import GeometryField


class DjangoGeoJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            d = datetime_safe.new_datetime(o)
            return d.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif isinstance(o, datetime.date):
            d = datetime_safe.new_date(o)
            return d.strftime(self.DATE_FORMAT)
        elif isinstance(o, datetime.time):
            return o.strftime(self.TIME_FORMAT)
        elif isinstance(o, decimal.Decimal):
            return float(o)
        elif isinstance(o, GEOSGeometry):
            return json.loads(o.geojson)
        else:
            return super(DjangoGeoJSONEncoder, self).default(o)


class Serializer(PythonSerializer):
    def start_serialization(self, queryset):
        self.feature_collection = {"type": "FeatureCollection", "features": []}
        self.feature_collection["crs"] = self.get_crs(queryset)
        self._current = None

    def get_crs(self, queryset):
        if self.crs == False:
            return None
        crs = {}
        srid = self.options.get("srid", None)
        if srid is None:
            field = self.get_geometry_field(queryset)
            srid = field.srid
            # obj = queryset[0]
            # geom = field._get_val_from_obj(obj)
            #srid = geom.srid
        crs["type"] = "link"
        properties = {}
        properties["href"] = "http://spatialreference.org/ref/epsg/%s/" % (str(srid))
        properties["type"] = "proj4"
        crs["properties"] = properties
        return crs

    def get_geometry_field(self, queryset):
        fieldname = self.options.get("fieldname", None)
        fields = queryset.model._meta.fields
        geometry_fields = [f for f in fields if isinstance(f, GeometryField)]
        if fieldname:
            fieldnames = [x.name for x in geometry_fields]
            try:
                field = geometry_fields[fieldnames.index(fieldname)]
            except IndexError:
                raise Exception("%s is not a valid geometry field on %s" % (fieldname, queryset.model.__class__.__name__))
        else:
            # We only currently support one geometry field
            field = geometry_fields[0]
        return field

    def start_object(self, obj):
        self._current = {"type": "Feature", "properties": {}}

    def end_object(self, obj):
        self.feature_collection["features"].append(self._current)
        self._current = None

    def end_serialization(self):
        self.options.pop('stream', None)
        self.options.pop('fields', None)
        self.options.pop('use_natural_keys', None)

        self.options.pop('crs', None)
        self.options.pop('srid', None)

        json.dump(self.feature_collection, self.stream, cls=DjangoGeoJSONEncoder, **self.options)

    def handle_field(self, obj, field):
        value = field._get_val_from_obj(obj)
        if is_protected_type(value):
            self._current['properties'][field.name] = value
        elif isinstance(value, GEOSGeometry):
            self._current['geometry'] = value
        else:
            self._current['properties'][field.name] = field.value_to_string(obj)

    def getvalue(self):
        if callable(getattr(self.stream, 'getvalue', None)):
            return self.stream.getvalue()

    def handle_fk_field(self, obj, field):
        related = getattr(obj, field.name)
        if related is not None:
            if self.use_natural_keys and hasattr(related, 'natural_key'):
                related = related.natural_key()
            else:
                if field.rel.field_name == related._meta.pk.name:
                    # Related to remote object via primary key
                    related = related._get_pk_val()
                else:
                    # Related to remote object via other field
                    related = smart_unicode(getattr(related, field.rel.field_name), strings_only=True)
        self._current['properties'][field.name] = related

    def handle_m2m_field(self, obj, field):
        if field.rel.through._meta.auto_created:
            if self.use_natural_keys and hasattr(field.rel.to, 'natural_key'):
                m2m_value = lambda value: value.natural_key()
            else:
                m2m_value = lambda value: smart_unicode(value._get_pk_val(), strings_only=True)
            self._current['properties'][field.name] = [m2m_value(related)
                               for related in getattr(obj, field.name).iterator()]

    def serialize(self, queryset, **options):
        """
        Serialize a queryset.
        """
        self.options = options

        self.stream = options.get("stream", StringIO())
        self.selected_fields = options.get("fields")
        self.use_natural_keys = options.get("use_natural_keys", False)

        self.crs = options.get("crs", True)

        self.start_serialization(queryset)

        opt = queryset.model._meta
        local_fields = queryset.model._meta.local_fields
        many_to_many_fields = queryset.model._meta.many_to_many

        for obj in queryset:
            self.start_object(obj)
            for field in local_fields:
                if field.serialize or field.primary_key:
                    if field.rel is None:
                        if self.selected_fields is None or field.attname in self.selected_fields:
                            self.handle_field(obj, field)
                    else:
                        if self.selected_fields is None or field.attname[:-3] in self.selected_fields:
                            self.handle_fk_field(obj, field)
            for field in many_to_many_fields:
                if field.serialize:
                    if self.selected_fields is None or field.attname in self.selected_fields:
                        self.handle_m2m_field(obj, field)
            self.end_object(obj)
        self.end_serialization()
        return self.getvalue()
