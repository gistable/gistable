# modified version of http://tomforb.es/using-python-metaclasses-to-make-awesome-django-model-field-choices
# that preserves order of definition

import inspect, itertools


class Option(object):
    _counter = itertools.count()
    def __init__(self, value, verbose_name=None):
        self._count = Option._counter.next()
        self.value = value
        self.verbose_name = verbose_name if verbose_name is not None else value

    def __repr__(self):
        return "Field(%r)" % self.value


class ChoiceBase(type):
    def __new__(cls, name, bases, attrs):
        new_class = super(ChoiceBase, cls).__new__(cls, name, bases, attrs)
        fields = [(key, value) for key, value in attrs.iteritems() if isinstance(value, Option)]
        new_class._data = sorted(fields, key=lambda item: item[1]._count)
        for field in fields:
            setattr(new_class, field[0], field[1].value)
        return new_class

    def __iter__(self):
        for value, data in self._data:
            yield data.value, data.verbose_name


class Choice(object):
    """
    Example:

        class GenderChoice(Choice):
            MALE = Option('male', _('male'))
            FEMALE = Option('female', _('female'))
    """
    __metaclass__ = ChoiceBase