# -*- coding: utf-8 -*-

import json


class ModelFactory(object):
    """Parse a JSONSchema and generate a class from it."""

    TYPES = {
        'string': str,
        'integer': int,
        'number': float,
        'boolean': bool,
        'object': dict,
        'array': list,
        'null': type(None),
        'any': object
    }

    def __init__(self, *args, **kwargs):
        super(ModelFactory, self).__init__(*args, **kwargs)

        self.cache = {}

    def get_cls(self, path):
        with open(path) as f:
            schema = json.load(f)

        schemaname = str(schema['$schema'])
        cls = self.cache.get(schemaname, None)

        if cls is None:
            base = ModelFactory.TYPES[schema['type']]
            members = self.get_members(schema)

            cls = type(schemaname, (base,), members)
            self.cache[schemaname] = cls

        return cls

    def get_members(self, schema):
        members = {
            '__doc__': schema.get('description', None)
        }

        if schema['type'] == 'object':
            for field in schema['properties']:
                fieldname = field.upper()
                desc = schema['properties'][field].get('description', None)
                default = schema['properties'][field].get('default', None)

                def get_property(fieldname, desc):
                    def fget(self):
                        attrname = getattr(self, fieldname)

                        if attrname not in self:
                            setattr(self, attrname, None)

                        return self[attrname]

                    def fset(self, value):
                        attrname = getattr(self, fieldname)

                        if value is None:
                            value = default

                        self[attrname] = value

                    def fdel(self):
                        attrname = getattr(self, fieldname)
                        del self[attrname]

                    return property(fget, fset, fdel, desc)

                members[fieldname] = field
                members[field] = get_property(fieldname, desc)

        return members
