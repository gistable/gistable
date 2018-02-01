import pdb
import sys
import re
class Combinators:
  def __init__ (self,input):
		self.input = input
		self.counter = 0

	# Consume a character (this assumes we don't have a scanner/lexer)
	def eat(self,c):
		if (self.input[0] == c):
			self.input = self.input[1:len(self.input)]
			self.counter += 1
		else:
			print("Expected %c but got %c at position %i", c, self.input[0], self.counter)

	# check to see if there is more
	def more(self):
		return len(self.input) > 0

	# look ahead
	def peek(self):
		if(self.more()):
			return self.input[0]
		return '\0'

	# advance to the next character
	def next(self):
		c = self.peek()
		self.eat(c)
		return c
class Builder:
	def __init__ (self):
		self.set = set({}) # create an empty dictionary that will be the set for the builder
	def visit(self, visitor):
		if isinstance(visitor, Nonterminal):
			if visitor not in self.set:
				self.set.add(visitor)
				visitor.rhs.accept(self)
		if isinstance(visitor, Terminal): pass
		if isinstance(visitor, Sequence):
			for parser in visitor.parsers:
				parser.accept(self)
		if isinstance(visitor, Or):
			for p in visitor.parsers:
				p.accept(self)
		if isinstance(visitor, Star):
			visitor.child.accept(self)
		if isinstance(visitor, Grammar): pass
class Printer:
	def visit(self,visitor):
		if isinstance(visitor, Nonterminal):
			return str(visitor.name)
		if isinstance(visitor, Terminal):
			ret_string = ""
			if isinstance(visitor,Symbol):
				ret_string = ""
				ret_string += "'"
				ret_string += visitor.symbol
				ret_string += "'"
			if isinstance(visitor,Integer):
				ret_string += "Integer"
			return ret_string
		if isinstance(visitor, Sequence):
			ret_string = ""
			for p in visitor.parsers:
				ret_string += " "
				ret_string += p.accept(self)
			return ret_string
		if isinstance(visitor, Star):
			ret_string = ""
			ret_string += "("
			ret_string += visitor.child.accept(self)
			ret_string += ")*"
			return ret_string
		if isinstance(visitor, Or):
			ret_string = ""
			for i,val in enumerate(visitor.parsers):
				ret_string += "("
				ret_string += val.accept(self)
				ret_string += ")"
				if(i + 1 != len(visitor.parsers)):
					ret_string += " | "
			return ret_string
		if isinstance(visitor, Grammar):
			ret_string = ""
			for n_term in visitor.nonterminals:
				ret_string += n_term.name
				ret_string += " ::= "
				ret_string += n_term.rhs.accept(self)
				ret_string += "\n"
			return ret_string
class RDParse:
	def __init__(self, parse_str):
		self.combinator = Combinators(parse_str)
	def visit(self, visitor):
		if isinstance(visitor, Terminal):
			if isinstance(visitor, Integer):
				if re.match('[0-9]+', self.combinator.peek()):
					return [self.combinator.next()]
				else:
					return None
			if isinstance(visitor, Symbol):
				if self.combinator.peek() == visitor.symbol:
					return [self.combinator.next()]
				else:
					return None
		if isinstance(visitor, Star):
			ret_val = visitor.child.accept(self)
			if ret_val is None:
				return []
			else:
				return ret_val
		if isinstance(visitor, Sequence):
			ret_list = []
			for v in visitor.parsers:
				ret_val = v.accept(self)
				if ret_val is None:
					return None
				elif isinstance(ret_val,list):
					ret_list.append(ret_val)
			return ret_list
		if isinstance(visitor, Or):
			for v in visitor.parsers:
				ret_val = v.accept(self)
				if isinstance(ret_val,list):
					return ret_val
			return None
		if isinstance(visitor, Nonterminal):
			return visitor.rhs.accept(self)
		if isinstance(visitor, Grammar):
			return visitor.start.accept(self)
class Parser(object):
    def accept(self, visitor):
        return visitor.visit(self)
class Nonterminal(Parser):
	def __init__ (self, name):
		self.name = name
	def derives(self, *parsers):
		self.rhs = Sequence(flatten(parsers))

class Terminal(Parser): pass
class Sequence(Parser):
	def __init__ (self, *parsers):
		self.parsers = flatten(parsers)
class Symbol(Terminal):
	def __init__(self,symbol):
		self.symbol = symbol
class Star(Parser):
	def __init__(self,child):
		self.child = child
class Or(Parser):
	def __init__ (self, *parsers):
		self.parsers = flatten(parsers)
class Integer(Terminal): pass
class Grammar(Parser):
	def __init__ (self,start):
		self.builder = Builder()
		self.start = start
		start.accept(self.builder)
		self.nonterminals = self.builder.set

def flatten(*args):
    output = []
    for arg in args:
        if hasattr(arg, '__iter__'):
            output.extend(flatten(*arg))
        else:
            output.append(arg)
    return output

def grammarExpr():
	group = Nonterminal("group")
	factor = Nonterminal("factor")
	term = Nonterminal("term")
	expression = Nonterminal("expression")

	# group       ::= '(' expression ')'
	group.derives(Symbol("("), expression, Symbol(")"))
	# factor      ::= integer | group
	factor.derives(Or(Integer(), group))
	# term        ::= factor (('*' factor) | ('/' factor))*
	term.derives(factor, Star(Or(Sequence(Symbol("*"), factor), Sequence(Symbol("/"), factor))))
	# expression  ::= term (('+' term) | ('-' term))*
	expression.derives(term, Star(Or(Sequence(Symbol("+"), term), Sequence(Symbol("-"), term))))

	return Grammar(expression)

if __name__ == '__main__':
	printer = Printer()
	parser = RDParse("1/3")
	parser2 = RDParse("(1+2)/3")
	parserParserNewParser = RDParse("3*(3+4*(3+1))")
	BuffaloBuffaloNewBuffalo = RDParse("8*(2*(3+4))+5")
	grammar = grammarExpr()
	print(grammar.accept(printer))
	print(grammar.accept(parser))
	print(grammar.accept(parser2))
	print(grammar.accept(parserParserNewParser))
	print(grammar.accept(BuffaloBuffaloNewBuffalo))