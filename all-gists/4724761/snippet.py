from json import JSONEncoder, loads
from time import mktime
from datetime import date, datetime
from google.appengine.ext import ndb
from google.appengine.ext.ndb import query


def to_epoch(value):
    """
    This is a view method to return the data in milli-seconds.

        :param value: Instance of `datetime.datetime`.
        :returns: `float` as the number of seconds since unix epoch.
    """
    return mktime(value.utctimetuple()) * 1000


def from_epoch(value):
    """
        :param value:
            Instance of `float` as the number of seconds since unix epoch.
        :returns:
            Instance of `datetime.datetime`.
    """
    return datetime.utcfromtimestamp(value / 1000)


def entity_to_dict(self, includes=None, excludes=None):
    """Encodes an `ndb.Model` to a `dict`. By default, only `ndb.Property`
    attributes are included in the result.

        :param include:
            List of strings keys of class attributes. Can be the name of the
            either a method or property.
        :param exclude:
            List of string keys to omit from the return value.
        :returns: Instance of `dict`.
        :raises: `ValueError` if any key in the `include` param doesn't exist.
    """
    value = ndb.Model.to_dict(self)
    # set the `id` of the entity's key by default..
    if self.key:
        value['key'] = self.key.urlsafe()
        value['id'] = self.key.id()
    if includes:
        for inc in includes:
            attr = getattr(self, inc, None)
            if attr is None:
                cls = self.__class__
                logging.warn('entity_to_dict cannot encode `%s`. Property is \
not defined on `%s.%s`.', inc, cls.__module__, cls.__name__)
                continue
            if callable(attr):
                value[inc] = attr()
            else:
                value[inc] = attr
    if excludes:
        # exclude items from the result dict, by popping the keys
        # from the dict..
        [value.pop(exc) for exc in excludes
            if exc in value]
    return value


def entity_from_dict(cls, value):
    """
        :param cls: `ndb.Model` subclass.
        :param value:
    """
    def _decode(_result, _value):
        """
        Deserializes `dict` values to `ndb.Property` values.
        """
        for key, val in _value.iteritems():
            prop = cls._properties.get(key)
            # logging.error('prop: %s', dir(prop))
            if prop is None:
                logging.warn('entity_from_dict cannot decode: `%s`. Property is \
not defined on: `%s.%s`.', key, cls.__module__, cls.__name__)
                continue
            if isinstance(prop, (ndb.DateTimeProperty, ndb.DateProperty,
                ndb.TimeProperty)):
                if prop._repeated:
                    val = [from_epoch(v) for v in val]
                else:
                    val = from_epoch(val)
            if isinstance(prop, ndb.BlobKeyProperty):
                if prop._repeated:
                    val = [ndb.BlobKey(urlsafe=v) for v in val]
                else:
                    val = ndb.BlobKey(urlsafe=val)
            if isinstance(prop, ndb.KeyProperty):
                if prop._repeated:
                    val = [ndb.Key(urlsafe=v) for v in val]
                else:
                    val = ndb.Key(urlsafe=val)
            if isinstance(prop, ndb.BlobProperty):
                pass
            _result[key] = val
        return _result
    return cls(**_decode({}, value))


def entity_from_json(cls, value):
    """
    Deserializes a json str to an instance of an `ndb.Model` subclass.

        :param cls: `ndb.Model` subclass.
        :param value:
    """
    value = loads(value, strict=False)
    if isinstance(value, list):
        result = [entity_from_dict(cls, v) for v in value]
    else:
        result = entity_from_dict(cls, value)
    return result
