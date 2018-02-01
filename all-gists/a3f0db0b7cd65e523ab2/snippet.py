
# This has been moved to a repo -- https://github.com/saucecode/postfix-calculator
# all future updates found there

#!/usr/bin/env python
# postfix.py - a postfix calculator for python 2 & 3
# version 5    2016-09-20

import string, math
import inspect

def countFunctionArguments(func):
	try:
		return len(inspect.signature(func).parameters)
	except:
		return len(inspect.getargspec(func).args)

def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

variables = {'pi':math.pi, 'e':math.e, '\\':1.0}
def variableAssign(a,b):
	variables[a] = variables[b] if b in variables else b
	if a[0] == '-':
		variables[a[1:]] = -1 * (variables[b] if b in variables else b)
	else:
		variables['-'+a] = -1 * (variables[b] if b in variables else b)
	return b

OPERATIONS = {
	'+' : lambda a,b:a+b,
	'-' : lambda a,b:b-a,
	'/' : lambda a,b:b/a,
	'*' : lambda a,b:a*b,
	'**' : lambda a,b:b**a,
	'sin' : lambda a:math.sin(a),
	'cos' : lambda a:math.cos(a),
	'tan' : lambda a:math.tan(a),
	'atan' : lambda a:math.atan(a),
	'asin' : lambda a:math.asin(a),
	'acos' : lambda a:math.acos(a),
	'sqrt' : lambda a:a**0.5,
	'%' : lambda a,b:b%a,
	'ln' : lambda a:math.log(a),
	'log' : lambda a,b:math.log(b,a),
	'rad' : lambda a:math.radians(a),
	'deg' : lambda a:math.degrees(a),
	'=' : variableAssign
}

def executeOp(opid, args):
	if opid == '=':
		return OPERATIONS[opid](*[float(i) if is_number(i) else i for i in args])
	else:
		return OPERATIONS[opid](*[variables[i] if i in variables else float(i) for i in args])

def doPostfix(postfix_string):
	calc = postfix_string.split(' ')
	if calc[0] == '': return
	
	stack = []
	for i in calc:
		if is_number(i) or i in variables:
			stack.append(i)
		elif i in OPERATIONS:
			argCount = countFunctionArguments(OPERATIONS[i])
			args=[]
			for ii in range(argCount):
				args.append(stack.pop(-1))
			ans = executeOp(i, args)
			stack.append(ans)
		else:
			stack.append(i)
	if len(stack) == 1:
		variables['\\'] = [variables[elm] if elm in variables else elm for elm in stack][0]
	return [variables[elm] if elm in variables else elm for elm in stack]

if __name__ == '__main__':
	print('saucecode\'s postfix v5    2016-09-20')

	try:
		raw_input
	except:
		raw_input = input

	while 1:
		try:
			output = doPostfix(raw_input('> '))
			print(' '.join([str(item) for item in output]))
		except TypeError as e:
			print('')
			continue