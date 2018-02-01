import zlib
from base64 import b64decode, b64encode

from django.db import models

# django-jsonfield
from jsonfield import JSONField


class CompressedJSONField(JSONField):
    """
    Django model field that stores JSON data compressed with zlib.
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, basestring):
            try:
                value = zlib.decompress(b64decode(value))
            except zlib.error:
                pass
        return super(CompressedJSONField, self).to_python(value)

    def get_db_prep_value(self, value, connection=None, prepared=None):
        value = super(CompressedJSONField, self).get_db_prep_value(value,
                                                                   connection,
                                                                   prepared)
        return b64encode(zlib.compress(value, 9))


# South support
try:
    from south.modelsinspector import add_introspection_rules
    # you may need to modify this regex to match where you install this file
    add_introspection_rules([], ['fields\.CompressedJSONField'])
except ImportError:
    pass