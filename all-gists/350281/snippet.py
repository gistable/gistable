from django.conf import settings
from django.db import models
from django.utils.encoding import smart_str

if hasattr(settings, 'USE_CPICKLE'):
    import cPickle as pickle
else:
    import pickle


class PickleField(models.TextField):
    """
    Custom field that enables to store pickled Python objects.
    """
    __metaclass__ = models.SubfieldBase

    editable = False
    serialize = False

    def get_db_prep_value(self, value):
        return pickle.dumps(value)

    def get_default(self):
        if self.has_default():
            if callable(self.default):
                return self.default()
            return self.default
        return super(PickleField, self).get_default()

    def to_python(self, value):
        if not isinstance(value, basestring):
            return value

        try:
            return pickle.loads(smart_str(value))
        except (EOFError, IndexError, KeyError, ValueError):
            return value


# Make able to store Django model objects in ``PickleField``
def picklefield(func):
    def wrapper(obj, field):
        if isinstance(field, PickleField):
            return field.get_db_prep_save(obj)
        return func(obj, field)
    return wrapper


models.Model.prepare_database_save = \
    picklefield(models.Model.prepare_database_save)
