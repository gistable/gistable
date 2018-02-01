""" This is a convenient way to monkeypatch a method or attribute of a Python
    object. This is great for situations where you want to modify a global
    object within a limited scope, i.e., your typical class or module when
    testing. This was tested and works with Python 2.7 and 3.4. """

import contextlib

@contextlib.contextmanager
def monkeypatched(object, name, patch):
    """ Temporarily monkeypatches an object. """

    pre_patched_value = getattr(object, name)
    setattr(object, name, patch)
    yield object
    setattr(object, name, pre_patched_value)

if __name__ == '__main__':

    class Foo:
        bar = False

    with monkeypatched(Foo, 'bar', True):
        assert Foo.bar

    assert not Foo.bar
    