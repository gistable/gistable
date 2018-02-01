# This function prints out all of the values and sub-values in any variable, including 
# lists, tuples and classes. It's not very efficient, so use it for testing/debugging
# purposes only. Examples are below:

#-------------------------------------------------------------------------------------

# ShowData(range(10))

# (list)
#    (int) 0
#    (int) 1
#    (int) 2
#    (int) 3
#    (int) 4
#    (int) 5
#    (int) 6
#    (int) 7
#    (int) 8
#    (int) 9

#-------------------------------------------------------------------------------------

# ShowData([[j for j in range(1, i)] for i in range(1, 5)])

# (list)
#
#    (list)
#
#    (list)
#       (int) 1
#
#    (list)
#       (int) 1
#       (int) 2
#
#    (list)
#       (int) 1
#       (int) 2
#       (int) 3

#---------------------------------------------------------------------------------------

# class example:
# 	x = 5
# 	y = 10.24
# 	z = 43.5
#
# ShowData(example())

# (instance)
#    (dict pair)(str)y : (float)10.24
#    (dict pair)(str)x : (int)5
#    (dict pair)(str)z : (float)43.5

#----------------------------------------------------------------------------------------

#(or use the 'index' keyword argument to show list indicies)
# ShowData(range(10), index=True)

# (list)
#   [0](int) 0
#   [1](int) 1
#   [2](int) 2
#   [3](int) 3
#   [4](int) 4
#   [5](int) 5
#   [6](int) 6
#   [7](int) 7
#   [8](int) 8
#   [9](int) 9


# Returns "int"/"float"/"list", etc.
def typeStr(variable):
	return str(type(data))[7: -2]

def ShowData(data, prefix='', **kargs):
	_type = typeStr(data)

	if type(data) in [None, bool, int, float, str]:
		print '{0}({1}) {2}'.format(prefix, _type, data)

	else:
		#Format dictionaries manually to get a nice looking result
		if type(data) is dict:
			for (key, value) in data.items():
				print '{0}(dict pair)({1}){2} : ({3}){4}'.format(prefix, typeStr(key), key, typeStr(value), value)

		#Normal iterators
		elif type(data) in [list, tuple, set]:
			print '\n{0}({1})'.format(prefix, _type)

			if 'index' in kargs and kargs['index']:
				for (number, i) in enumerate(data):
					ShowData(i, prefix + '{0}  [{1}]'.format(prefix, number))
			else:
				for i in data:
					ShowData(i, prefix + '{0}    '.format(prefix))

		#any other, non-common class
		else:
			print '\n{0}({1})'.format(prefix, _type)

			# Destructure instance so we can print what's inside
			pairs = dict((name, getattr(data, name)) for name in dir(data) if not name.startswith('__'))	
			ShowData(pairs, prefix + '   ')