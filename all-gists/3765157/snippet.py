''' metatuple - Recursive namedtuple from arbitrary dict

After 2 hours of intensive coding and some tequila sips I found
a "simple" solution to create a namedtuple from any dictionary,
recursivelly creating any necessary namedtuple.

Probably there are tons of easiest ways of doing that, like some
well documented method or standart function in the python library,
but that wouldn't be fun.'''

from collections import namedtuple

def metatuple(name, attrs):
	'''Creates a namedtuple from an arbitrary dict,
	recursivelly namedtuple()ing any dict it finds on the way.

	>>> person = {
	...     'name': 'Charlotte',
	...     'address': {
	...             'street': 'Acacia Avenue',
	...             'number': 22,
	...     },
	... }
	>>> Person = metatuple('Person', person)
	>>> charlotte = Person(**person)
	>>> assert charlotte.name == 'Charlotte'
	>>> assert charlotte.address.street == 'Acacia Avenue'
	>>> assert charlotte.address.number == 22

	# ensure dict's random key ordering don't affect correctness
	>>> rand_dict = {
	...     'a_field0': 0,
	...     'b_field1': 1,
	...     'c_field2': 2,
	...     'd_field3': 3,
	...     'e_field4': 4,
	...     'f_field5': 5,
	...     'g_field6': 6,
	... }
	>>> RandDict = metatuple('RandDict', rand_dict)
	>>> rand = RandDict(**rand_dict)
	>>> assert rand.a_field0 == 0
	>>> assert rand.b_field1 == 1
	>>> assert rand.c_field2 == 2
	>>> assert rand.d_field3 == 3
	>>> assert rand.e_field4 == 4
	>>> assert rand.f_field5 == 5
	>>> assert rand.g_field6 == 6
	'''

	class _meta_cls(type):
		'''Metaclass to replace namedtuple().__new__ with a recursive version _meta_new().'''
		def __new__(mcs, name, bases, metadict):
			def _meta_new(_cls, **kv):
				return tuple.__new__(_cls, ([ (metatuple('%s_%s' % (_cls.__name__, k), kv[k].keys())(**kv[k]) if isinstance(kv[k], dict) else kv[k]) for k in _cls._fields]))
			metadict['__new__'] = _meta_new
			return type.__new__(mcs, bases[0].__name__, bases, metadict)

	class _metabase(namedtuple(name, ' '.join(attrs))):
		'''Wrapper metaclass for namedtuple'''
		__metaclass__ = _meta_cls

	return _metabase

if __name__ == "__main__":
	import doctest
	doctest.testmod()
