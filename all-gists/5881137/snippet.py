import re

from rest_framework import serializers, renderers, parsers


class JSONRenderer(renderers.JSONRenderer):
    def render(self, data, *args, **kwargs):
        if data:
            data = recursive_key_map(underscore_to_camelcase, data)
        return super(JSONRenderer, self).render(data, *args, **kwargs)


class JSONParser(parsers.JSONParser):
    def parse(self, *args, **kwargs):
        obj = super(JSONParser, self).parse(*args, **kwargs)
        return recursive_key_map(camelcase_to_underscore, obj)


def underscore_to_camelcase(word, lower_first=True):
    result = ''.join(char.capitalize() for char in word.split('_'))
    if lower_first:
        return result[0].lower() + result[1:]
    else:
        return result

_first_cap_re = re.compile('(.)([A-Z][a-z]+)')
_all_cap_re = re.compile('([a-z0-9])([A-Z])')


# http://stackoverflow.com/a/1176023
def camelcase_to_underscore(word):
    s1 = _first_cap_re.sub(r'\1_\2', word)
    return _all_cap_re.sub(r'\1_\2', s1).lower()


def recursive_key_map(function, obj):
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.iteritems():
            if isinstance(key, basestring):
                key = function(key)
            new_dict[key] = recursive_key_map(function, value)
        return new_dict
    if hasattr(obj, '__iter__'):
        return [recursive_key_map(function, value) for value in obj]
    else:
        return obj