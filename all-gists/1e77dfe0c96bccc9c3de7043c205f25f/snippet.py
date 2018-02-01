import platform
import ctypes


print("Implementation: %s" % platform.python_implementation())


def cell_set(cell, target):
    offset = 2 if platform.python_implementation() == 'PyPy' else 4
    def inner():
        return (lambda: target).__closure__[0]
    p_cell = ctypes.cast(id(cell), ctypes.POINTER(ctypes.c_int))
    p_target_cell = ctypes.cast(id(inner()), ctypes.POINTER(ctypes.c_int))
    import pdb;pdb.Pdb()  # prevent pypy from optimizing out
    p_cell[offset] = p_target_cell[offset]


def f():
    a = 'ayy'

    def g():
        cell_set((lambda: a).__closure__[0], 'lmao')

    g()
    return a


print(f())