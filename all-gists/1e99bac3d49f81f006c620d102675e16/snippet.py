#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    Copyright © 2017 Manoel Vilela
#
#    @project: Pipelines in Python
#     @author: Manoel Vilela
#      @email: manoel_vilela@engineer.com
#


from functools import partial


class Infix(object):

    def __init__(self, func):
        self.func = func

    def __or__(self, other):
        return self.func(other)

    def __ror__(self, other):
        return Infix(partial(self.func, other))

    def __call__(self, v1, v2):
        return self.func(v1, v2)


@Infix
def pipe(x, f):
    return f(x)


def example():
    range(1, 10) |pipe| sum |pipe| (lambda x: x + 10) |pipe| print # 55
