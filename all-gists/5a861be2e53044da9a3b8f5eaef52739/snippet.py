from enum import Enum
from functools import reduce
from collections import Iterable


def auto_str(cls):
    def build_key_value_str(key, value, intent):
        return build_intent(intent) + key + ': ' + value + '\n'

    def is_enum(obj):
        return isinstance(obj, Enum)

    def is_iterable(obj):
        return isinstance(obj, Iterable)

    def is_primitive(obj):
        return type(obj) in (int, float, bool, str)

    def build_intent(intent):
        return reduce(lambda p, c: p + ' ', range(intent), '')

    def format_enum(value):
        return value.name

    def format_primitive(obj):
        return str(obj)

    def format_iterable(value, intent):
        return '\n'.join(format_obj_str(t, intent + 2) for t in value)

    def format_obj_str(obj, intent):
        if is_enum(obj):
            return format_enum(obj)
        elif is_primitive(obj):
            return format_primitive(obj)
        else:
            return format_obj(obj, intent)

    def format_obj(obj, intent):
        temp = ""
        for key in iter(obj.__dict__):
            value = obj.__dict__[key]
            if is_enum(value):
                temp += build_key_value_str(key, format_enum(value), intent)
            elif is_primitive(value):
                temp += build_key_value_str(key, str(value), intent)
            elif is_iterable(value):
                temp += build_key_value_str(key, '\n' + format_iterable(value, intent), intent)
            else:
                obj_str = format_obj(value, intent + 2)
                temp += build_key_value_str(key, '\n' + obj_str, intent)
        return temp

    def __str__(self):
        return format_obj_str(self, 0)

    cls.__str__ = __str__
    return cls
