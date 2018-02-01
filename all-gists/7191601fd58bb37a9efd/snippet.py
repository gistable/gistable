# -*- coding: utf-8 -*-

import functools
import logging
import time

from django.conf import settings
from django.db import connection


logger = logging.getLogger(__name__)


class timer(object):

    def __init__(self, prefix):
        self._start = None
        self._prefix = prefix

    def __enter__(self):
        self._start = time.time()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if settings.DEBUG:
            logger.debug(
                u'[timer] %s %s', self._prefix, time.time() - self._start)

    def __call__(self, fn):

        @functools.wraps(fn)
        def inner(*args, **kwargs):
            with self:
                return fn(*args, **kwargs)
        return inner


class debug_sql(object):

    def __init__(self, prefix):
        self._prefix = prefix
        self._start = self._end = None

    def __enter__(self):
        self._start = len(connection.queries)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._end = len(connection.queries)
        if not settings.DEBUG:
            return
        for stat in connection.queries[self._start:self._end]:
            if isinstance(stat, dict):
                logger.debug('[debug_sql %s] time %s query %s',
                             self._prefix, stat['time'], stat['sql'])
            else:
                logger.debug('[debug_sql %s] %s', self._prefix, stat)
            logger.debug('')
        logger.debug('[debug_sql %s] num of queries: %s',
                     self._prefix, self._end - self._start)

    def __call__(self, fn):

        @functools.wraps(fn)
        def inner(*args, **kwargs):
            with self:
                return fn(*args, **kwargs)
        return inner