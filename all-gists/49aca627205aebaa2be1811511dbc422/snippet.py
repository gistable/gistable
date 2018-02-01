#!/usr/bin/env python

from lib.core.data import kb
from lib.core.enums import PRIORITY
import string

__priority__ = PRIORITY.NORMAL

def dependencies():
    pass

def tamper(payload, **kwargs):
    orig = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    srvr = "QqnPvka03wMU6ZybjmK4BRSEWdVishgClpI1AouFNOJ9zrtL2Yef7Tc8GxDHX5"
    return payload.translate(string.maketrans(orig,srvr))
