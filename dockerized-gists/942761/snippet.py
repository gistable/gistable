"""
Patches the database wrapper and template engine to throw an exception if a query is executed inside of a template.

In your urls.py, enable it like so:

>>> import monkey
>>> monkey.patch_templates()
"""

import logging
import types

from threading import local

def replace_call(func):
    def inner(callback):
        def wrapped(*args, **kwargs):
            return callback(func, *args, **kwargs)

        actual = getattr(func, '__wrapped__', func)
        wrapped.__wrapped__ = actual
        wrapped.__doc__ = getattr(actual, '__doc__', None)
        wrapped.__name__ = actual.__name__

        _replace_function(func, wrapped)
        return wrapped
    return inner

def _replace_function(func, wrapped):
    if isinstance(func, types.FunctionType):
        if func.__module__ == '__builtin__':
            # oh shit
            __builtins__[func] = wrapped
        else:
            module = __import__(func.__module__, {}, {}, [func.__module__], 0)
            setattr(module, func.__name__, wrapped)
    elif getattr(func, 'im_self', None):
        # TODO: classmethods
        raise NotImplementedError
    elif hasattr(func, 'im_class'):
        # for unbound methods
        setattr(func.im_class, func.__name__, wrapped)
    else:
        raise NotImplementedError

_state = local()

def patch_templates():
    if getattr(_state, 'patched', False):
        return

    from django.db.backends import BaseDatabaseWrapper
    from django import template

    class QueryInTemplate(Exception):
        pass

    class TemplateCursorWrapper(object):
        def __init__(self, cursor, connection):
            self.cursor = cursor
            self.connection = connection
            self.logger = logging.getLogger('monkey.template.queries')

        def truncate(self, sql, maxlen=100):
            if len(sql) > maxlen:
                sql = sql[:maxlen-3] + '...'
            return sql

        def execute(self, sql, params=()):
            if getattr(_state, 'rendering', False):
                self.logger.warning('Query seen in %s: %s', _state.rendering.name, self.truncate(sql), extra={'sql': sql, 'params': params})
            return self.cursor.execute(sql, params)

        def executemany(self, sql, paramlist):
            if getattr(_state, 'rendering', False):
                self.logger.warning('Query seen in %s: %s', _state.rendering.name, self.truncate(sql), extra={'sql': sql, 'params': paramlist})
            return self.cursor.executemany(sql, paramlist)

        def __getattr__(self, attr):
            if attr in self.__dict__:
                return self.__dict__[attr]
            else:
                return getattr(self.cursor, attr)

        def __iter__(self):
            return iter(self.cursor)

    @replace_call(template.Template.render)
    def render(func, self, context):
        if not getattr(_state, 'rendering', False):
            _state.rendering = self
            try:
                return func(self, context)
            finally:
                _state.rendering = False
        else:
            return func(self, context)

    @replace_call(BaseDatabaseWrapper.cursor)
    def cursor(func, self):
        result = func(self)

        return TemplateCursorWrapper(result, self)
    
    _state.patched = True