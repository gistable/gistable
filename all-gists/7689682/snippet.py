#!/usr/bin/env python3
import string

class PartialFormatter(string.Formatter):
    def __init__(self, missing='~'):
        self.missing = missing

    def get_field(self, field_name, args, kwargs):
        # Handle missing fields
        try:
            return super().get_field(field_name, args, kwargs)
        except (KeyError, AttributeError):
            return None, field_name

    def format_field(self, value, spec):
        if value is None:
            return self.missing
        else:
            return super().format_field(value, spec)

fmt=PartialFormatter()
data = {'n': 3, 'k': 3.141594, 'p': {'a': 7, 'b': 8}}
print(fmt.format('{n}, {k:.2f}, {p[a]}, {p[b]}', **data))
# 3, 3.14, 7, 8
del data['k']
data['p']['b'] = None
print(fmt.format('{n}, {k:.2f}, {p[a]:.2f}, {p[b]}', **data))
# 3, ~, 7.00, ~
