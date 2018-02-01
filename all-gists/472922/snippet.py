# -*- coding: utf-8 -*-

from django.db import models


class LtreeField(models.CharField):
    """Field implementation of PostgreSQL ltree type"""

    def __init__(self, *args, **kwds):
        super(LtreeField, self).__init__(max_length=128, *args, **kwds)
    
    def db_type(self, connection):
        engine = connection.settings_dict['ENGINE']
        if 'postgresql' not in engine:
            # TODO - better database check
            raise TypeError("ltree is PostgreSQL specific type")
        return 'ltree'


class LtreeHelper(object):
    ATTR_OPERATOR_MAP = (
        ('startswith', '<@'),
        ('atmost', '@>'),
        ('like', '~'),
    )
    def __init__(self, manager):
        self.manager = manager
        self.ltree_field = None

    def prepare(self):
        if self.ltree_field:
            return
        for field in self.manager.model._meta.fields:
            if isinstance(field, LtreeField):
                self.ltree_field = field
                break
        if self.ltree_field is None:
            raise TypeError("LtreeManager is available only for tables "
                    "containing PostgreSQL ltree type column")
        self.sql_lookup_mapping = {}
        for suffix, operator in self.ATTR_OPERATOR_MAP:
            attr_name = '%s__%s' % (self.ltree_field.name, suffix)
            self.sql_lookup_mapping[attr_name] = operator

    def sql_lookup_prepare_value(self, value):
        value = value.replace("'", "\\'")
        return "'%s'" % value

    def to_sql(self, lookup_token, value):
        operator = self.sql_lookup_mapping.get(lookup_token, None)
        if operator is None:
            lookup_name = lookup_token.split('__', 1)[1]
            raise TypeError("Lookup token no supported: %s" % lookup_name)
        value = self.sql_lookup_prepare_value(value)
        return "%s %s %s" % (self.ltree_field.name, operator, value)


class LtreeManager(models.Manager):
        
    def __init__(self, *args, **kwds):
        self._ltree = LtreeHelper(self)
        super(LtreeManager, self).__init__(*args, **kwds)

    def filter(self, *args, **kwds):
        # TODO: -  better LtreeHelper initialization would be nice
        self._ltree.prepare()
        ltree_token = '%s__' % self._ltree.ltree_field.name
        ltree_kwds = {}
        # check all kwds and remove those related to ltree
        for lookup_token, value in kwds.items():
            if lookup_token.startswith(ltree_token):
                kwds.pop(lookup_token)
                ltree_kwds[lookup_token] = value
        # create query_set, withoult ltree related arguments
        query_set = super(LtreeManager, self).filter(*args, **kwds)
        where = []
        # create additional where statement, related to given ltree params
        for name, value in ltree_kwds.iteritems():
            where.append(self._ltree.to_sql(name, value))
        return query_set.extra(where=where)
