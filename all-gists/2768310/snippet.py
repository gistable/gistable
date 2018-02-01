''' A model field to store and retrieve Google Protocol Buffer objects easily.

Uses the BlobField available on GAE for storage.

Usage:

    myfield = ProtobufField(protoclass=MyProtocolClass)

where MyProtocolClass is a protocol descriptor class generated from a .proto file.
The field is supposed to store only the given kind of protocol messages.

The `protoclass` attribute is required.
'''
from django.db import models
from djangotoolbox.fields import BlobField

class ProtobufField(BlobField):
    description = "Storage for protobuffer objects"
    __metaclass__ = models.SubfieldBase

    def __init__(self, protoclass, *args, **kwargs):
        self.protoclass = protoclass
        super(ProtobufField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, self.protoclass):
            return value

        protobuf = self.protoclass()
        protobuf.ParseFromString(value)
        return protobuf

    def get_prep_value(self, value):
        return value.SerializeToString()

    def get_db_prep_value(self, value, connection, prepared=False):
        if hasattr(value, "SerializeToString"):
            value = value.SerializeToString()
        return super(ProtobufField, self).get_db_prep_value(value=value, connection=connection, prepared=prepared)

    def value_to_string(self, obj):
        obj = obj.SerializeToString()
        return super(ProtobufField, self).value_to_string(obj)
