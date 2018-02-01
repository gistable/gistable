'''
Extremely Simple Django Template Tags!
'''

from django.template import Library, Node, TemplateSyntaxError, resolve_variable
from django.utils.translation import ugettext as _
register = Library()

class GenericTNode(Node):
	def __init__(self, parts):
		self.parts = parts
	def render(self, context):
		pointer = self.parts.pop(0)
		global _tag_reg
		if pointer in _tag_reg:
			return _tag_reg[pointer](self.parts, context)
		else:
			raise TemplateSytnaxError, "GenericTNode was called with an non-registered tag"

def do_template_tag(parser,token):
	'''
	DO NOT USE! USED AUTOMATICALLY BY TEMPLATE TAG!!!!!
	'''
	parts = token.contents.split()
	return GenericTNode(parts)

_tag_reg = {}

def template_tag(pointer):
	'''
	Example:
	@template_tag("Tag_name")
	def fjiowehtnowe(parts, context):
		work
		return output
	'''
	def decorator(function):
		global register, _tag_reg
		_tag_reg[pointer] = function
		register.tag(pointer,do_template_tag)
		return function
	return decorator