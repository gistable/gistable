# -*- coding: utf-8 -*-

import memcache
import random


NS_KEY_RANGE_MAX = 1000000

mc = memcache.Client(['127.0.0.1:11211'], debug=0)


def clear_ns(ns):
    mc.incr(_compute_ns_key(ns))


def _compute_key(key, ns=None):
    if ns:
        return '%s_%d_%s' % (ns, get_ns_key(ns), str(key),)
    return key


def _compute_ns_key(ns):
    return '%s_ns_key' % ns


def get(key, ns=None):
    return mc.get(_compute_key(key, ns))


def get_ns_key(ns):
    ns_key = mc.get(_compute_ns_key(ns))
    if not ns_key:
        ns_key = random.randint(1, NS_KEY_RANGE_MAX)
        mc.set(_compute_ns_key(ns), ns_key)
    return ns_key


def set(key, val, ns=None, **kwargs):
    return mc.set(_compute_key(key, ns), val, **kwargs)


mc.flush_all()
assert get('blah') == None
set('blah', 2)
assert get('blah') == 2

assert get('blah', ns='foo') == None
set('blah', 8, ns='foo')
assert get('blah', ns='foo') == 8
assert get('blah') == 2

clear_ns('foo')
assert get('blah', ns='foo') == None
assert get('blah') == 2
