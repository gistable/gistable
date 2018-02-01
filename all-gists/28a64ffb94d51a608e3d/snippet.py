import ctypes
from ctypes import pythonapi as api
import sys
from types import (BuiltinFunctionType, GetSetDescriptorType, FrameType,
                   MemberDescriptorType, MethodType)

import guppy
from guppy.heapy import Path

hp = guppy.hpy()

def _w(x):
    def f():
        x
    return f

CellType = type(_w(0).func_closure[0])

del _w

# -----------------------------------------------------------------------------

def _write_struct_attr(addr, value, add_offset):
        ptr_size = ctypes.sizeof(ctypes.py_object)
        ptrs_in_struct = (3 if hasattr(sys, "getobjects") else 1) + add_offset
        offset = ptrs_in_struct * ptr_size + ctypes.sizeof(ctypes.c_ssize_t)
        ref = ctypes.byref(ctypes.py_object(value))
        ctypes.memmove(addr + offset, ref, ptr_size)

def _replace_attribute(source, rel, new):
    if isinstance(source, (MethodType, BuiltinFunctionType)):
        if rel == "__self__":
            # Note: PyMethodObject->im_self and PyCFunctionObject->m_self
            # have the same offset
            _write_struct_attr(id(source), new, 1)
            return
        if rel == "im_self":
            return  # Updated via __self__
    if isinstance(source, type):
        if rel == "__base__":
            return  # Updated via __bases__
        if rel == "__mro__":
            return  # Updated via __bases__ when important, otherwise futile
    if isinstance(source, (GetSetDescriptorType, MemberDescriptorType)):
        if rel == "__objclass__":
            _write_struct_attr(id(source), new, 0)
            return
    try:
        setattr(source, rel, new)
    except TypeError as exc:
        print "Unknown R_ATTRIBUTE (read-only):", rel, type(source)

def _replace_indexval(source, rel, new):
    if isinstance(source, tuple):
        temp = list(source)
        temp[rel] = new
        replace(source, tuple(temp))
        return
    source[rel] = new

def _replace_indexkey(source, rel, new):
    source[new] = source.pop(source.keys()[rel])

def _replace_interattr(source, rel, new):
    if isinstance(source, CellType):
        api.PyCell_Set(ctypes.py_object(source), ctypes.py_object(new))
        return
    if rel == "ob_type":
        source.__class__ = new
        return
    print "Unknown R_INTERATTR:", rel, type(source)

def _replace_local_var(source, rel, new):
    source.f_locals[rel] = new
    api.PyFrame_LocalsToFast(ctypes.py_object(source), ctypes.c_int(0))

_RELATIONS = {
    Path.R_ATTRIBUTE: _replace_attribute,
    Path.R_INDEXVAL: _replace_indexval,
    Path.R_INDEXKEY: _replace_indexkey,
    Path.R_INTERATTR: _replace_interattr,
    Path.R_LOCAL_VAR: _replace_local_var
}

def _path_key_func(path):
    reltype = type(path.path[1]).__bases__[0]
    return 1 if reltype is Path.R_ATTRIBUTE else 0

def replace(old, new):
    for path in sorted(hp.iso(old).pathsin, key=_path_key_func):
        relation = path.path[1]
        try:
            func = _RELATIONS[type(relation).__bases__[0]]
        except KeyError:
            print "Unknown relation:", relation, type(path.src.theone)
            continue
        func(path.src.theone, relation.r, new)

# -----------------------------------------------------------------------------

class A(object):
    def func(self):
        return self

class B(object):
    pass

class X(object):
    pass

def sure(obj):
    def inner():
        return obj
    return inner

def gen(obj):
    while True:
        yield obj

class S(object):
    __slots__ = ("p", "q")

class T(object):
    __slots__ = ("p", "q")

class U(object):
    pass

class V(object):
    pass

class W(U):
    pass

# -----------------------------------------------------------------------------

a = A()
b = B()

X.cattr = a
x = X()
x.iattr = a
d = {a: a}
L = [a]
t = (a,)
f = a.func
meth = a.__sizeof__
clo = sure(a)
g = gen(a)
s = S()
s.p = a
u = U()
ud = U.__dict__["__dict__"]
s.q = S
sd = S.q

# -----------------------------------------------------------------------------

def examine_vars(id1, id2, id3):
    ex = lambda v, id_: str(v) + ("" if id(v) == id_ else " - ERROR!")
    print "dict (local var):  ", ex(a, id1)
    print "dict (class attr): ", ex(X.cattr, id1)
    print "dict (inst attr):  ", ex(x.iattr, id1)
    print "dict (key):        ", ex(d.keys()[0], id1)
    print "dict (value):      ", ex(d.values()[0], id1)
    print "list:              ", ex(L[0], id1)
    print "tuple:             ", ex(t[0], id1)
    print "method (instance): ", ex(f(), id1)
    print "method (builtin):  ", ex(meth.__self__, id1)
    print "closure:           ", ex(clo(), id1)
    print "frame (generator): ", ex(next(g), id1)
    print "slots:             ", ex(s.p, id1)
    print "class (instance):  ", ex(type(u), id2)
    print "class (subclass):  ", ex(W.__bases__[0], id2)
    print "class (g/s descr): ", ex(ud.__get__(u, U) or type(u), id2)
    print "class (mem descr): ", ex(sd.__get__(s, S), id3)

if __name__ == "__main__":
    examine_vars(id(a), id(U), id(S))
    print "-" * 35
    replace(a, b)
    replace(U, V)
    replace(S, T)
    print "-" * 35
    examine_vars(id(b), id(V), id(T))
