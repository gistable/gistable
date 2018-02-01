import hashlib
import logging

from werkzeug import cached_property
from flask.signals import Namespace
from ndb import model, tasklets, query, key
from ndb.key import Key as BaseKey


class Error(Exception):
    """Base exception for model module"""


signals = Namespace()

pre_put = signals.signal('pre-put')
post_put = signals.signal('post-put')

pre_delete = signals.signal('pre-delete')
post_delete = signals.signal('post-delete')


class Unique(model.Model):
    @classmethod
    def create(cls, value):
        entity = cls(key=model.Key(cls, value))
        txn = lambda: entity.put() if not entity.key.get() else None
        return model.transaction(txn) is not None

    @classmethod
    def create_multi(cls, values):
        keys = [model.Key(cls, value) for value in values]
        entities = [cls(key=key) for key in keys]
        func = lambda e: e.put() if not e.key.get() else None
        created = [model.transaction(lambda: func(e)) for e in entities]

        if created != keys:
            # A poor man's rollback: delete all recently created records.
            model.delete_multi(k for k in created if k)
            return False, [k.id() for k in keys if k not in created]

        return True, []


class Key(BaseKey):
    def __new__(cls, *_args, **kwargs):
        if _args:
            if len(_args) == 1 and isinstance(_args[0], dict):
                assert not kwargs
                kwargs = _args[0]
            else:
                assert 'flat' not in kwargs
                kwargs['flat'] = _args
        self = object.__new__(cls)
        self.__reference = key._ConstructReference(cls, **kwargs)
        return self

    @cached_property
    def class_model(self):
        return model.Model._kind_map.get(self.kind())

    def delete_async(self, *args, **kwargs):
        self._pre_delete()
        fut = super(Key, self).delete_async(*args, **kwargs)
        fut.add_callback(self._post_delete)
        return fut

    def _pre_delete(self):
        pre_delete.send(self.class_model, key=self)

    def _post_delete(self):
        post_delete.send(self.class_model, key=self)

key.Key = Key
model.Key = Key


class MetaModel(model.MetaModel):
    def __new__(cls, name, bases, classdict):
        classdict['Unique'] = type(name + 'Unique', (Unique,), {})
        new_class = super(MetaModel, cls).__new__(cls, name, bases, classdict)
        return new_class

    def __init__(cls, name, bases, classdict):
        super(MetaModel, cls).__init__(name, bases, classdict)
        cls._register_unique_events()


class Model(model.Model):
    __metaclass__ = MetaModel

    query_class = query.Query

    @classmethod
    def _query(cls, *args, **kwds):
        qry = cls.query_class(kind=cls._get_kind(), **kwds)
        if args:
            qry = qry.filter(*args)
        return qry
    query = _query

    def _put_async(self, *args, **kwargs):
        creation = not self._has_complete_key()
        self._pre_put(creation=creation)
        fut = super(Model, self)._put_async(*args, **kwargs)
        fut.add_callback(self._post_put, created=creation)
        return fut
    put_async = _put_async

    def _pre_put(self, creation=False):
        self.pre_put(creation=creation)
        pre_put.send(self.__class__, instance=self, creation=creation)

    def pre_put(self, creation=False):
        pass

    def _post_put(self, created=False):
        self.post_put(created=created)
        post_put.send(self.__class__, instance=self, created=created)

    def post_put(self, created=False):
        pass

    @classmethod
    def _register_unique_events(cls):
        @pre_put.connect_via(cls)
        def check_unique_constraints(send, instance=None, **kwargs):
            instance._check_unique_constraints()

        @pre_delete.connect_via(cls)
        @tasklets.tasklet
        def delete_unique_values(sender, key=None, **kwargs):
            instance = yield key.get_async()
            if not instance:
                logging.error(
                    'pre_delete: Can not get instance for key %r' % key)
                return
            instance._delete_unique_values()

    @property
    def _unique_values(self):
        for props in self.Meta.unique:
            hsh = hashlib.md5()
            values = {}
            for prop in props:
                values[prop] = getattr(self, prop)
            hsh.update(repr(values))
            hsh = hsh.hexdigest()
            yield values, hsh

    def _check_unique_constraints(self):
        for values, hsh in self._unique_values:
            if not self.Unique.create(hsh):
                raise UniqueConstraintError(values)

    def _delete_unique_values(self):
        for values, hsh in self._unique_values:
            model.Key(self.Unique, hsh).delete_async()


class ChangedPropsMixin(object):
    @classmethod
    def _from_pb(cls, *args, **kwargs):
        ent = super(ChangedPropsMixin, cls)._from_pb(*args, **kwargs)
        ent._orig_values = ent._values.copy()
        return ent

    def prop_changed(self, *props, **kwargs):
        _all = kwargs.pop('all', False)
        if not hasattr(self, '_orig_values'):
            return True
        changes = [self._values[prop] != self._orig_values[prop]
                   for prop in props]
        func = all if _all else any
        return func(changes)


class UniqueConstraintError(Error):
    """Raised when unique constraint is violated"""

    def __init__(self, values):
        self.values = values
        Error.__init__(self,
            'Unique constraint violated for values %r' % values)
