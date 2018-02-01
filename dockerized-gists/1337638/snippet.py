# A simple formatter for bpython to work with Pygments.
# Pygments really kicks ass, it made it really easy to
# get the exact behaviour I wanted, thanks Pygments. :)
#
# License blah blah blah.
# Bob Farrell.
#
from pygments.formatter import Formatter
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic, Token, Whitespace, Literal, Punctuation

"""These format strings are pretty ugly.
\x01 represents a colour marker, which
	can be proceded by one or two of
	the following letters:
	k, r, g, y, b, m, c, w, d
	Which represent:
	blacK, Red, Green, Yellow, Blue, Magenta,
	Cyan, White, Default
	e.g. \x01y for yellow,
		\x01gb for green on blue background

\x02 represents the bold attribute

\x03 represents the start of the actual
	text that is output (in this case it's
	a %s for substitution)

\x04 represents the end of the string; this is
	necessary because the strings are all joined
	together at the end so the parser needs them
	as delimeters

"""

f_strings = {
	Keyword : "\x01y\x03%s\x04",
	Name : "\x01w\x02\x03%s\x04",
	Comment : "\x01b\x03%s\x04",
	String : "\x01m\x03%s\x04",
	Error : "\x01r\x03%s\x04",
	Literal : "\x01r\x03%s\x04",
	Literal.String : "\x01m\x03%s\x04",
	Token.Literal.Number.Float : "\x01g\x02\x03%s\x04",
	Number : "\x01g\x03%s\x04",
	Operator : "\x01c\x02\x03%s\x04",
	Operator.Word : "\x01c\x02\x03%s\x04",
	Punctuation : "\x01c\x02\x03%s\x04",
	Generic : "\x01d\x03%s\x04",
	Token : "\x01g\x03%s\x04",
	Whitespace : "\x02d\x03%s\x04"
}

class BPythonFormatter( Formatter ):
	"""This is the custom formatter for bpython.
	Its format() method receives the tokensource
	and outfile params passed to it from the
	Pygments highlight() method and slops
	them into the appropriate format string
	as defined above, then writes to the outfile
	object the final formatted string.

	See the Pygments source for more info; it's pretty
	straightforward."""

	def __init__(self, **options):
		Formatter.__init__(self, **options)
	
	def format( self, tokensource, outfile ):
		o = ''
		for token, text in tokensource:
			if text == '\n':
				continue

			if token in f_strings:
				o += f_strings[ token ] % text
			else:
				o += f_strings[ Token ] % text
		outfile.write( o.rstrip() )
