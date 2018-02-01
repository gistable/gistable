#!/usr/bin/python
"""Utility functions to work with character patterns."""

__lower_alpha = 'abcdefghijklmnopqrstuvwxyz'
__upper_alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
__numeric = '0123456789'

def pattern_create(length, charsets=None):
	"""Generates a unique, nonrepeating pattern of a given length.

	length:
		the resulting pattern's length, in characters

	charsets: 
		if given, must be a tuple/list containing 3 strings. The pattern
		will be generated using the given sets.

	"""
	if charsets is None:
		charsets = (__upper_alpha, __lower_alpha, __numeric)
	if length <= 0:
		return ''

	state = [0, 0, 0]
	output = []
	count = (length + 2) // 3
	while count > 0:
		output.append(charsets[0][state[0]] 
			+ charsets[1][state[1]] 
			+ charsets[2][state[2]])
		state[2] += 1
		if state[2] >= len(charsets[2]):
			state[2] = 0
			state[1] += 1
			if state[1] >= len(charsets[1]):
				state[1] = 0
				state[0] += 1
				if state[0] >= len(charsets[0]):
					state[0] = 0
					# print 'WARNING: the sequence has started over.'
		count -= 1
	return ''.join(output)[:length]

# Handy command-line usage
if __name__ == '__main__':
	import sys

	op = sys.argv[1]

	if op == 'make':
		length = int(sys.argv[2])
		print pattern_create(length)
	elif op == 'find':
		value = sys.argv[2]
		max_len = int(sys.argv[3])
		print 'Value provided: %s' % value

		if len(value) == 8:
			print 'Considering the value to be a hex register data'
			value = value.upper()
			chars = [chr(int(value[0:2], 16)),
				chr(int(value[2:4], 16)),
				chr(int(value[4:6], 16)),
				chr(int(value[6:8], 16))]
		elif len(value) == 4:
			print 'Considering the value to be a string'
			chars = value
		pat = pattern_create(max_len)
		pos = pat.find(''.join(chars))
		if pos == -1:
			chars = chars[::-1]
			pos = pat.find(''.join(chars))
			if pos == -1:
				print 'Not found (tried both BE and LE)'
			else:
				print 'Found (LE order) at offset %d' % pos
		else:
			print 'Found (BE order) at offset %d' % pos
