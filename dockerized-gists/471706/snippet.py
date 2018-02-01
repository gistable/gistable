import os
import re

def find(expression, path='.', type='df'):
	"""
	Find files or directories.
	
	>>> list(find(r'.*\.py$', type='f'))
	['./find.py']
	"""
	for base, directories, files in os.walk(path):
		if 'd' in type:
			for directory in directories:
				if re.match(expression, os.path.join(base, directory)):
					yield os.path.join(base, directory)
		if 'f' in type:
			for file in files:
				if re.match(expression, os.path.join(base, file)):
					yield os.path.join(base, file)
