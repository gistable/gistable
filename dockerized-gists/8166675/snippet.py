class Token:
	def __init__(self, value, type):
		self.value = value
		self.type = type

	def __repr__(self):
		return '{}({}, {})'.format(self.__class__.__name__, repr(self.value), repr(self.type))

class PatternError(ValueError):
	pass

class Lexer:
	def __init__(self, patterns, ignore_pattern=None):
		for pattern, _ in patterns:
			if pattern.match(''):
				raise PatternError('Pattern matches empty string')
		if ignore_pattern and ignore_pattern.match(''):
			raise PatternError('Ignore pattern matches empty string')
		self.patterns = patterns
		self.ignore_pattern = ignore_pattern

	def lex(self, string):
		cursor = 0
		line_number = 1
		column_number = 0
		while cursor < len(string):
			try:
				match = self.ignore_pattern.match(string, cursor)
			except AttributeError:
				pass
			else:
				if match is not None:
					line_number += match.group().count('\n')
					cursor = match.end()
					line_start = string.rfind('\n', 0, cursor) + 1
					if line_start == 0:
						column_number = 0
					else:
						column_number = match.end() - line_start
					continue

			for pattern, type in self.patterns:
				match = pattern.match(string, cursor)
				if match is not None:
					line_number += match.group().count('\n')
					cursor = match.end()
					line_start = string.rfind('\n', 0, cursor) + 1
					if line_start == 0:
						column_number = 0
					else:
						column_number = match.end() - line_start
					yield Token(match.group(), type)
					break
			else:
				start = string.rfind('\n', 0, cursor) + 1
				stop = string.find('\n', cursor)
				if stop == -1:
					stop = len(string)
				print(string[start:stop])
				from sys import stderr
				raise SyntaxError('unexpected token at line {}, column {}'.format(line_number, column_number))
