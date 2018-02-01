#!/usr/bin/env python
# -*- coding: utf-8 -*-

class AttrDict(dict):
    def __init__(self, arg=(), **kwargs):
        items = arg.items() if isinstance(arg, (dict, )) else arg
        for key, value in items:
            self[key] = self.fromdict(value)
        for key, value in kwargs.items():
            self[key] = self.fromdict(value)

    def __getattr__(self, name):
        try:
            value = self[name]
        except (KeyError, ):
            raise AttributeError(name)
        value = self[name] = self.fromdict(value)
        return value

    def __setattr__(self, name, value):
        self[name] = self.fromdict(value)

    #def __setitem__(self, key, value):
        #super(AttrDict, self).__setitem__(key, self.fromdict(value))

    @classmethod
    def fromdict(cls, value):
        return cls(value) if isinstance(value, (dict, )) else value