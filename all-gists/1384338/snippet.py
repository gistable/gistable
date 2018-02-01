"""''.format_map() in Python 2.x"""

try: 
    ''.format_map({})
except AttributeError: # Python < 3.2
    import string
    def format_map(format_string, mapping, _format=string.Formatter().vformat):
        return _format(format_string, None, mapping)
    del string

    #XXX works on CPython 2.6
    # http://stackoverflow.com/questions/2444680/how-do-i-add-my-own-custom-attributes-to-existing-built-in-python-types-like-a/2450942#2450942
    import ctypes as c

    class PyObject_HEAD(c.Structure):
        _fields_ = [
            ('HEAD', c.c_ubyte * (object.__basicsize__ -  c.sizeof(c.c_void_p))),
            ('ob_type', c.c_void_p)
        ]

    _get_dict = c.pythonapi._PyObject_GetDictPtr
    _get_dict.restype = c.POINTER(c.py_object)
    _get_dict.argtypes = [c.py_object]

    def get_dict(object):
        return _get_dict(object).contents.value

    get_dict(str)['format_map'] = format_map
else: # Python 3.2+
    def format_map(format_string, mapping):
        return format_string.format_map(mapping)

# test
import unittest

class FormatMapTestCase(unittest.TestCase):
    def test_format_map(self):
        self._test_format_map(lambda s, *args: s.format_map(*args))

    def test_function_format_map(self):
        self._test_format_map(format_map)

    def _test_format_map(self, format_map):
        # taken from Python source code
        self.assertEqual(format_map('', {}), '')
        self.assertEqual(format_map('a', {}), 'a')
        self.assertEqual(format_map('ab', {}), 'ab')
        self.assertEqual(format_map('a{{', {}), 'a{')
        self.assertEqual(format_map('a}}', {}), 'a}')
        self.assertEqual(format_map('{{b', {}), '{b')
        self.assertEqual(format_map('}}b', {}), '}b')
        self.assertEqual(format_map('a{{b', {}), 'a{b')

        # using mappings
        class Mapping(dict):
            def __missing__(self, key):
                return key
        self.assertEqual(format_map('{hello}', Mapping()), 'hello')
        self.assertEqual(format_map('{a} {world}', Mapping(a='hello')), 'hello world')

        class InternalMapping:
            def __init__(self):
                self.mapping = {'a': 'hello'}
            def __getitem__(self, key):
                return self.mapping[key]
        self.assertEqual(format_map('{a}', InternalMapping()), 'hello')


        class C:
            def __init__(self, x=100):
                self._x = x
            def __format__(self, spec):
                return spec
        self.assertEqual(format_map('{foo._x}', {'foo': C(20)}), '20')

        # test various errors
        self.assertRaises(TypeError, format_map,  '{')
        self.assertRaises(TypeError, format_map,  '}')
        self.assertRaises(TypeError, format_map, 'a{')
        self.assertRaises(TypeError, format_map, 'a}')
        self.assertRaises(TypeError, format_map, '{a')
        self.assertRaises(TypeError, format_map, '}a')

        self.assertRaises(ValueError, format_map,  '{', {})
        self.assertRaises(ValueError, format_map,  '}', {})
        self.assertRaises(ValueError, format_map, 'a{', {})
        self.assertRaises(ValueError, format_map, 'a}', {})
        self.assertRaises(ValueError, format_map, '{a', {})
        self.assertRaises(ValueError, format_map, '}a', {})

        # issue #12579: can't supply positional params to format_map
        self.assertRaises(ValueError, format_map, '{}', {'a' : 2})
        self.assertRaises(ValueError, format_map, '{}', 'a')
        self.assertRaises(ValueError, format_map, '{a} {}', {"a" : 2, "b" : 1})


if __name__=="__main__":
    unittest.main()
