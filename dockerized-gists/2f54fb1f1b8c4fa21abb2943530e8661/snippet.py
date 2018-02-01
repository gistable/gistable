#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import functools
import time


class throttle(object):
    u"""Ограничивает количество вызовов обёрнутой функции за указанный период времени."""

    def __init__(self, limit=3, period=60):
        self._limit = limit
        self._period = period
        self._reset()

    def _reset(self):
        self._counter = self._limit
        self._point = time.time()

    def __call__(self, func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            now = time.time()
            if self._point < now - self._period:
                self._reset()
            elif self._counter == 0:
                return
            self._counter -= 1
            return func(*args, **kwargs)
        return wrapped


if __name__ == '__main__':

    @throttle(limit=3, period=10)
    def print_now():
        print(time.time())

    for i in range(100):
        print_now()
        time.sleep(1)
