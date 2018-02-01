class DotDict(dict):
    """ A dictionary whose attributes are accessible by dot notation.

    This is a variation on the classic `Bunch` recipe (which is more limited
    and doesn't give you all of dict's methods). It is just like a dictionary,
    but its attributes are accessible by dot notation in addition to regular
    `dict['attribute']` notation. It also has all of dict's methods.

    .. doctest::

        >>> dd = DotDict(foo="foofoofoo", bar="barbarbar")
        >>> dd.foo
        'foofoofoo'
        >>> dd.foo == dd['foo']
        True
        >>> dd.bar
        'barbarbar'
        >>> dd.baz
        >>> dd.qux = 'quxquxqux'
        >>> dd.qux
        'quxquxqux'
        >>> dd['qux']
        'quxquxqux'

    NOTE:   There are a few limitations, but they're easy to avoid
            (these should be familiar to JavaScript users):

        1.  Avoid trying to set attributes whose names are dictionary methods,
            for example 'keys'. Things will get clobbered. No good.
        2.  You can store an item in a dictionary with the key '1' (`foo['1']`),
            but you will not be able to access that attribute using dotted
            notation if its key is not a valid Python variable/attribute name
            (`foo.1` is not valid Python syntax).

    FOR MORE INFORMATION ON HOW THIS WORKS, SEE:
    - http://stackoverflow.com/questions/224026/
    - http://stackoverflow.com/questions/35988/
    """

    def __getattr__(self, attr):
        return self.get(attr, None)

    __setattr__ = dict.__setitem__

    __delattr__ = dict.__delitem__