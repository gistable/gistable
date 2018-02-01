from decimal import Decimal
try:
    import simplejson as json
except ImportError:
    import json

from django.utils.functional import Promise


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles more data types than the default encoder.

    It adds support for:
      * date/datetime/time instances.
      * Decimal numbers.
      * Iterators.
      * Django translatable strings.

    Usage:
        >>> import datetime
        >>> data = {
        ...    'date': datetime.date(2001, 12, 10),
        ...    'decimal': Decimal('42.0'),
        ...    'iterator': xrange(10),
        ... }
        >>> json.dumps(data, cls=CustomJSONEncoder)
        '{"date": "2001-12-10", "decimal": "42.0", "iterator": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}'

    If Django compatibility is not wanted remove the lines about Promise.

    """

    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return unicode(obj)
        elif isinstance(obj, Promise):
            return force_unicode(obj)
        try:
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return super(CustomJSONEncoder, self).default(obj)