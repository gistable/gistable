#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import contextmanager


@contextmanager
def ctxmgr():
    print('before')

    def inner_generator():
        while True:
            print((yield))

    generator = inner_generator()
    next(generator)
    yield generator
    print('after')

if __name__ == '__main__':
    with ctxmgr() as c:
        c.send('inner')