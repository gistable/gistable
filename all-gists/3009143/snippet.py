import json
import datetime
from decimal import Decimal
from mongoengine.queryset import queryset_manager
from mongoengine.queryset import QuerySet
from mongoengine.base import BaseList, BaseDict, ObjectId


def list_encoder(inst, obj, field, force_string=False):
    """
    Encoder for iterable datatypes.
    """
    if force_string:
        return [str(x) for x in obj]
    return [inst.default(x, field) for x in obj]


def dict_encoder(inst, obj, field, force_string=False):
    """
    Encoder for dictinary like data type
    """
    data = {}
    for key in obj.keys():
        if force_string:
            data[key] = str(obj[key])
        else:
            data[key] = inst.default(obj[key], field)
    return data


def data_encoder(inst, obj, field, force_string=False):
    """
    Encoder for regular data types.
    """
    if force_string:
        return str(obj)
    return obj


def object_id_encoder(inst, obj, field, force_string=False):
    """
    Encoder for ObjectId
    """
    return str(obj)


def model_encoder_factory(
    fields={},
    extra_encoders={},
    reference_only_fields={}):
    """
    This will return a custom json.JSONEncoder class that is will be
    able to serialize a mongoengine queryset, or a iterable of
    querysets.

    fields: A dictionary, keys are data types, values are lists of
    fields for each data types, to be serialized. Fields can be
    attributes or object methods.
    example:
    {
        AdCategory: ['title', 'slug'],
        Region: ['name'],
    }

    extra_encoders: Contribute or override default encoders.
    example:
    {
        MySpecialDataType: my_function_that_encodes,
        MyOtherSpecialDataType: my_other_function_that_encodes,
    }

    reference_only_fields: Use this to avoid circular relations. This
    will result in the serialized data to contain a string
    representation of the object instead of a json representation.
    {
        Region: ['neighboring_regions'],
    }

    >>> from .models import AdCategory
    >>> from .geo.models import Region
    >>> from .utils import model_encoder_factory
    >>> import json
    >>> data = {
    ...     'regions': Region.objects.all(),
    ...     'categories': AdCategory.objects.all(),
    ...     }
    >>> fields = {
    ...     Region: ['name' ],
    ...     AdCategory: ['title', ],
    ...     }
    >>> enc = model_encoder_factory(fields=fields)
    >>> json.dumps(data, cls=enc)
    """

    # These encoders are matched by datatype. Still need to figure out
    # whether it's faster to match using a hash or with isinstance().
    encoders = {
        BaseList: list_encoder,
        QuerySet: list_encoder,
        list: list_encoder,
        tuple: list_encoder,
        BaseDict: dict_encoder,
        dict: dict_encoder,
        int: data_encoder,
        long: data_encoder,
        unicode: data_encoder,
        Decimal: data_encoder,
        datetime.datetime: data_encoder,
        datetime.date: data_encoder,
        ObjectId: object_id_encoder,
        }

    # When creating your encoder by calling this factory, you may
    # supply an extra_encoders parameter that will either contribute
    # to, or override existing encoders.
    encoders.update(extra_encoders)

    # Caching keys. Not sure if it's necessary to be honest.
    encoders_keys = encoders.keys()

    class Encoder(json.JSONEncoder):

        def default(self, obj, field=None):
            """
            This a function is called by json.dumps
            """

            # Get object type
            obj_type = type(obj)
            if obj_type in encoders_keys:
                # If the object type exists in encoders, checker
                # whether it is included in reference_only_fields, if
                # yes, the encoder will force the result to be a
                # string (or a list of strings) instead of an object,
                # or list of objects.
                force_string=False
                if (reference_only_fields and obj
                    and obj_type in reference_only_fields
                    and field in reference_only_fields[obj_type]):
                    force_string = True


                # Get the encoder and return its result. (The encoder
                # is given self, because it may recurse for iterable
                # items.)
                return encoders[obj_type](
                    self,
                    obj,
                    field,
                    force_string=force_string,
                    )

            # Now if the object type exists in fields, and the obj has
            # not matched any datatypes in the list of encoders,
            # create a dictionary of {field: value}.
            if obj_type in fields:
                data = {}
                for field in fields[obj_type]:
                    # This is called again because it needs to convert
                    # the value using encoders.
                    data[field] = self.default(
                        getattr(obj, field),
                        field,
                        )
                return data
            elif callable(obj):
                # If a supplied field is a callable, return the
                # callable result.
                return obj()
            else:
                # Finally if the field doesn't match anything, return
                # it's string representation.
                return {str(obj_type): None}
    return Encoder


class Serializable(object):
    """
    Your model can inherit from Serializable, it will get the
    json_tree method that will automatically use the model's _fields
    to attempt serialization.

    example:

    MyModel(Document, Serializable)
        title = StringField()

    then you can get all documents in a json structure by calling
    MyModel.json_tree()

    You should probably override the json_default_query method to
    customize the current queryset.

    You can also pass a queryset as an argument like so:
    MyModel.json_tree(MyModel.objects.filter(title='test'))
    """

    @classmethod
    def json_default_query(cls):
        return cls.objects.all()

    @classmethod
    def json_tree(cls, qs=None, fields={}, reference_only_fields={}):
        if qs == None:
            qs = cls.json_default_query()

        if not fields:
            fields = {cls: cls._fields.keys()}

        encoder = model_encoder_factory(
            fields=fields,
            reference_only_fields=reference_only_fields,
            )

        return json.dumps(
            qs,
            cls=encoder,
            )