from collections import MutableSet, MutableMapping, Mapping

class DataType(object):
    def __init__(self, value=None, context=None):
        if value is not None:
            self._check_value(value)
            self.value = value
        if context:
            self.context = context

    @property
    def value(self):
        return self.value

    @property
    def context(self):
        return self.context

    def to_op(self):
        raise NotImplementedError

    @classmethod
    def _check_value(value):
        raise NotImplementedError

class Counter(DataType):
    value = 0
    _increment = 0

    def increment(self, amount=1):
        self.value += amount
        self._increment += amount

    def decrement(self, amount=1):
        self.increment(-amount)

    def to_op(self):
        if self._increment != 0:
            return ('increment', self._increment)

    @classmethod
    def _check_value(value):
        if not isinstance(value, int):
            raise TypeError("Counter values must be integers")

class Register(DataType):
    _changed = False

    def set(self, value):
        self._check_value(value)
        if value != self.value:
            self._changed = True
            self.value = value

    def to_op(self):
        if self._changed:
            return self.value

    @classmethod
    def _check_value(value):
        if not isinstance(value, basestring):
            raise TypeError("Register values must be strings")

class Flag(DataType):
    value = False
    _changed = False

    def enable(self):
        self.value = True
        self._changed = not self._changed

    def disable(self):
        self.value = False
        self._changed = not self._changed

    def to_op(self):
        if self._changed:
            if self.value:
                return 'enable'
            else:
                return 'disable'

    @classmethod
    def _check_value(value):
        if not isinstance(value, bool):
            raise TypeError("Flag values must be bools")

class Set(MutableSet, DataType):
    value = set()
    _adds = set()
    _removes = set()

    # DataType API
    @classmethod
    def _check_value(value):
        for element in value:
            if not isinstance(element, basestring):
                raise TypeError("Set elements must be strings")

    def to_op(self):
        if self._adds or self._removes:
            {'adds': list(self._adds),
             'removes': list(self._removes)}

    # MutableSet API
    def __contains__(self, element):
        return element in self.value

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def add(self, element):
        if not isinstance(element, basestring):
            raise TypeError("Set elements must be strings")

        if element in self._removes:
            self._removes.discard(element)
        else:
            self._adds.add(element)
        self.value.add(element)

    def discard(self, element):
        if element in self._adds:
            self._adds.discard(element)
        else:
            self._removes.add(element)
        self.value.discard(element)

_type_mappings = {
    'COUNTER': Counter,
    'FLAG': Flag,
    'REGISTER': Register,
    'SET': Set,
    'MAP': Map
    }
