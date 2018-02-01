import copy

from cerberus import Validator
from cerberus import errors

from collections import Mapping, Sequence


class ObjectValidator(Validator):
    def __init__(self, *args, **kwargs):
        self.allow_unknown = True
        super(ObjectValidator, self).__init__(*args, **kwargs)

    def validate_object(self, obj):
        return self.validate(obj.__dict__)

    def _validate_type_object(self, field, value):
        # objects which are not Mapping or Sequence types are allowed.
        # (Mapping and Sequence types are dealt elsewhere.)
        if not (isinstance(value, object) and \
                not isinstance(value, (Sequence, Mapping))):
            self._error(field, errors.ERROR_BAD_TYPE % "object")

    def _validate_schema(self, schema, field, value):
        if isinstance(value, (Sequence, Mapping)):
            super(ObjectValidator, self)._validate_schema(schema, field, value)
        elif isinstance(value, object):
            validator = copy.copy(self)
            validator.schema = schema
            validator.validate(value.__dict__, context=self.document)
            if len(validator.errors):
                self._error(field, validator.errors)