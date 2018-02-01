"""
module mydjangolib.bigint_patch

A fix for the rather well-known ticket #399 in the django project.

Create and link to auto-incrementing primary keys of type bigint without
having to reload the model instance after saving it to get the ID set in
the instance.

Logs:
- v1.0: Created by Florian
- v1.1: Updated by Thomas
  * Fixed missing param `connection`
  * Used endswith for engine type check 
    (for better compatibility with `dj_database_url` and heroku)  
  * Added support for sqlite3 (which uses BIGINT by default)
  * Added south's add_introspection_rules if south is defined
  * Added BigOneToOneField and a short description
  * Assumed file location: common/fields.py
"""

from django.core import exceptions
from django.conf import settings
from django.db.models import fields
from django.utils.translation import ugettext as _
from south.modelsinspector import add_introspection_rules
from django.db.models.fields.related import OneToOneField

__version__ = "1.1"
__author__ = "Florian Leitner"
__author__ = "Thomas Yip @ BeeDesk"

class BigIntegerField(fields.IntegerField):
    def db_type(self, connection):
        if settings.DATABASE_ENGINE.endswith('mysql'):
            return "bigint"
        elif settings.DATABASE_ENGINE.endswith('oracle'):
            return "NUMBER(19)"
        elif settings.DATABASE_ENGINE.endswith('postgres'):
            return "bigint"
        elif settings.DATABASE_ENGINE.endswith('sqlite3'):
            return super(BigIntegerField, self).db_type(connection)
        else:
            raise NotImplemented
    
    def get_internal_type(self):
        return "BigIntegerField"
    
    def to_python(self, value):
        if value is None:
            return value
        try:
            return long(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                _("This value must be a long integer."))

class BigAutoField(fields.AutoField):
    def db_type(self, connection):
        if settings.DATABASE_ENGINE.endswith('mysql'):
            return "bigint AUTO_INCREMENT"
        elif settings.DATABASE_ENGINE.endswith('oracle'):
            return "NUMBER(19)"
        elif settings.DATABASE_ENGINE.endswith('postgres'):
            return "bigserial"
        elif settings.DATABASE_ENGINE.endswith('sqlite3'):
            return super(BigAutoField, self).db_type(connection)
        else:
            raise NotImplemented

    def get_internal_type(self):
        return "BigAutoField"
    
    def to_python(self, value):
        if value is None:
            return value
        try:
            return long(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                _("This value must be a long integer."))

class BigForeignKey(fields.related.ForeignKey):
    
    def db_type(self, connection):
        rel_field = self.rel.get_related_field()
        # next lines are the "bad tooth" in the original code:
        if (isinstance(rel_field, BigAutoField) or
                (not connection.features.related_fields_match_type and
                isinstance(rel_field, BigIntegerField))):
            # because it continues here in the django code:
            # return IntegerField().db_type()
            # thereby fixing any AutoField as IntegerField
            return BigIntegerField().db_type(connection)
        return rel_field.db_type(connection)

class BigOneToOneField(BigForeignKey, OneToOneField):
    """
    If you use subclass model, you might need to name 
    the `ptr` field explicitly. This is the field type you 
    might want to use. Here is an example: 
    
    class Base(models.Model):
        title = models.CharField(max_length=40, verbose_name='Title')

    class Concrete(Base):
        base_ptr = fields.BigOneToOneField(Base)
        ext = models.CharField(max_length=12, null=True, verbose_name='Ext')
    """
    pass

if 'south' in settings.INSTALLED_APPS:
    add_introspection_rules([], ['^common\.fields\.BigIntegerField'])
    add_introspection_rules([], ['^common\.fields\.BigAutoField'])
    add_introspection_rules([], ['^common\.fields\.BigForeignKey'])
    add_introspection_rules([], ['^common\.fields\.BigOneToOneField'])

