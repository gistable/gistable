import ctypes

PyFrame_LocalsToFast = ctypes.pythonapi.PyFrame_LocalsToFast
PyFrame_LocalsToFast.argtypes = [ctypes.py_object]

# Doing this with cython instead of ctypes would be much easier (and more
# robust). I just do it this way to keep the example self-contained.
frameobject_fields = [
    # PyObject_VAR_HEAD
    ("ob_refcnt", ctypes.c_int64),
    ("ob_type", ctypes.py_object),
    ("ob_size", ctypes.c_ssize_t),
    # struct _frame *f_back;      /* previous frame, or NULL */
    ("f_back", ctypes.c_void_p),
    # PyCodeObject *f_code;       /* code segment */
    ("f_code", ctypes.c_void_p),
    # PyObject *f_builtins;       /* builtin symbol table (PyDictObject) */
    ("f_builtins", ctypes.py_object),
    # PyObject *f_globals;        /* global symbol table (PyDictObject) */
    ("f_globals", ctypes.py_object),
    ]
import sys
if hasattr(sys, "getobjects"):
    # This python was compiled with debugging enabled.
    frameobject_fields = [
        ("_ob_next", ctypes.c_void_p),
        ("_ob_prev", ctypes.c_void_p),
        ] + frameobject_fields
class PyFrameObject(ctypes.Structure):
    _fields_ = frameobject_fields

def set_globals_dict(frame, new_globals):
    # f_globals *must* point to a real PyDictObject
    assert isinstance(new_globals, dict)
    ct_frame = PyFrameObject.from_address(id(frame))
    assert id(ct_frame.f_globals) == id(frame.f_globals)
    ct_frame.f_globals = new_globals
    assert id(new_globals) == id(frame.f_globals)

class DataFrameContextManager(object):
    """A context manager that works like R's with() function.

    The usage is like this:

       with DataFrameContextManager(df):
         <your code here>

    Then <your code here> can refer to any columns in the data frame `df` as
    ordinary local variables. `df` can actually be any dict-like object.

    There are a few caveats:
    * You cannot re-assign any of these local variables. (You can, however,
    modify them in place. `x = ...` is illegal; `x[:] = ...` is fine.)
    * You cannot re-assign *any* global variables from within the `with`
    block. Normally this is not an issue; the only way you could possibly do
    this would be by using the `global` keyword.
    * These local variables are even more ephemeral than ordinary local
    variables. If you use `pdb.post_mortem` to debug an exception raised from
    inside the `with` block, then these variables will have
    disappeared. Defining a closure inside one of these `with` blocks will
    have curious and probably undesireable effects.
    """

    def __init__(self, df):
        self.df = df
        # A unique sentinel value, that can be used identify undefined
        # variables (as distinct from those that are defined to be None,
        # etc.):
        self.NOTHING = object()

    def __enter__(self):
        from inspect import currentframe
        self.caller_frame = currentframe(1)
        # We would really like to 'interpose' a new scope into the name lookup
        # chain.
        #
        # Wrinkle 1: there are actually two lookup chains; Python determines
        # at compile-time whether each variable is local or global, and uses a
        # different lookup procedure for each.
        #
        # Wrinkle 2: We can interpose a new scope into the global lookup
        # chain, but not the local lookup chain. Therefore we have to modify
        # the local namespace in-place, and then pull any changes out again by
        # hand.
        #
        # Wrinkle 3: because of optimizations Python does for local lookups,
        # we have to use an obscure C API call to actually modify the local
        # lookup dictionary.
        #
        # XX: does this work with nested scopes?
        self.names = list(self.df)
        # You might think that Python local variables were stored in a dict,
        # as per locals() or the .f_locals attribute of frame objects. The
        # dict is a lie. Actually they are stored in a hidden array inside the
        # frame object, two API functions are used to make the dict lie work.
        # PyFrame_FastToLocals: extracts local variable values into the
        # .f_locals dict.  PyFrame_LocalsToFast: copies the local variable
        # values from the .f_locals dict into the hidden array.
        # PyFrame_FastToLocals is called implicitly whenever we access the
        # .f_locals attribute of a frame. Therefore, it is a good idea to save
        # it in a temporary variable and use that, so as to avoid accidentally
        # overwriting any changes we make:
        locals_ = self.caller_frame.f_locals
        # Variables that are compiled as local, but not yet assigned, will not
        # appear in the .f_locals array. So we need to get the real list of
        # local variable names:
        self.local_names = [name
                            for name in self.caller_frame.f_code.co_varnames
                            if name in self.names]
        self.shadowed_locals = {}
        for name in self.local_names:
            self.shadowed_locals[name] = locals_.get(name, self.NOTHING)
            locals_[name] = self.df[name]
        # This propagates the locals_ dictionary to the magical array that
        # Python actually uses to store local variables.
        PyFrame_LocalsToFast(self.caller_frame)

        # Needed to undo our hack later
        self.real_globals = self.caller_frame.f_globals
        self.new_globals = dict(self.real_globals)
        self.new_globals.update(self.df.iteritems())
        # Needed to detect attempts to re-assign global variables
        self.orig_global_ids = {}
        for k, v in self.new_globals.iteritems():
            self.orig_global_ids[k] = id(v)
        set_globals_dict(self.caller_frame, self.new_globals)

    def __exit__(self, exc_type, value, traceback):
        locals_ = self.caller_frame.f_locals
        # Before we do anything else (esp. anything that might fail), unwind
        # our scope hack:
        end_locals = dict(locals_)
        for name, value in self.shadowed_locals.iteritems():
            if value is self.NOTHING and name in locals_:
                del locals_[name]
            else:
                locals_[name] = value
        PyFrame_LocalsToFast(self.caller_frame)
        set_globals_dict(self.caller_frame, self.real_globals)
        # Next, check if the user was naughty and tried to re-assign any
        # data-frame variables, or any globals at all. This indicates a simple
        # bug in their code, and overrides any exception raised from inside
        # the 'with' block.
        for key, value in self.new_globals.iteritems():
            if id(value) != self.orig_global_ids.get(key):
                raise (NameError,
                       "illegal assignment to global %r in"
                       " DataFrameContextManager scope"
                       % (key,))
        for name in self.local_names:
            if end_locals.get(name, self.NOTHING) is not self.df[name]:
                raise NameError(
                       "illegal re-assignment of magic local variable"
                       " %r in DataFrameContextManager scope"
                       % (name,))
        # False means, any exception which was raised by the 'with' block
        # should be re-raised.
        return False

import numpy as np
_global_def = "_global_def"
# This avoids annoyances with reload():
if "_global_undef" in globals():
    del _global_undef
def test_with_data():
    assert _global_def == "_global_def"
    local_init = "local_init"
    assert local_init == "local_init"
    data = {"_global_def": [1],
            "local_init": [2],
            "local_unset": [3],
            "_global_undef": [4],
            }
    # import pandas
    # df = pandas.DataFrame(data)
    df = data
    with DataFrameContextManager(df):
        assert np.all(_global_def == [1])
        assert np.all(local_init == [2])
        assert np.all(local_unset == [3])
        assert np.all(_global_undef == [4])
    assert _global_def == "_global_def"
    assert "_global_undef" not in globals()
    assert local_init == "local_init"
    assert "local_unset" not in locals()
    
    assert np.all(df["_global_def"] == [1])
    assert np.all(df["local_init"] == [2])
    assert np.all(df["local_unset"] == [3])
    assert np.all(df["_global_undef"] == [4])

    # Check error exit
    try:
        with DataFrameContextManager(df):
            raise IOError, "just kidding"
    except IOError, e:
        assert e.args == ("just kidding",)
    else:
        assert False
    assert _global_def == "_global_def"
    assert "_global_undef" not in globals()
    assert local_init == "local_init"
    assert "local_unset" not in locals()

    # Check that attempts to re-assign variables are caught.
    try:
        with DataFrameContextManager(df):
            global _bad_global_
            _bad_global_ = object()
    except NameError:
        pass
    else:
        assert False
    try:
        with DataFrameContextManager(df):
            local_init = [22]
    except NameError:
        pass
    else:
        assert False
    assert local_init == "local_init"

    # This pointless assignment is what makes this a local variable.
    local_unset = "local_unset"

if __name__ == "__main__":
    import nose
    nose.runmodule()

