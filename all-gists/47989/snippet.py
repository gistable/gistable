"""
Scanner: match text to generate tokens.
Adam Blinkinsop <blinks@acm.org>

First, construct a scanner with the tokens you'd like to match described as
keyword arguments, using Python-syntax regular expressions.
WARNING: Group syntax in these expressions has an undefined effect.

>>> simple = Scan(ID=r'\w+')

You can now use this object to generate tokens by calling it with one or more
strings.

>>> tokens = list(simple('hello'))
>>> len(tokens), tokens[0]
(1, Token("ID -> 'hello'"))
>>> print simple
ID -> \\w+

Characters that don't match will raise an exception with the location of the
error (see http://www.gnu.org/prep/standards/html_node/Errors.html).

>>> tokens = list(simple('hello world'))
Traceback (most recent call last):
  ...
UnrecognizedCharacter: 1.5: couldn't match ' '
>>> len(tokens), tokens[0]
(1, Token("ID -> 'hello'"))

>>> simple = Scan(ID=r'\w+', SPACE=r'\s+')
>>> list(simple('hello world'))
[Token("ID -> 'hello'"), Token("SPACE -> ' '"), Token("ID -> 'world'")]

You can also ignore tokens to keep them from being generated.

>>> simple.ignore('SPACE')
>>> list(simple('hello world'))
[Token("ID -> 'hello'"), Token("ID -> 'world'")]

While this scanner doesn't keep track of lines 
"""
import re


class Error(Exception):
  """The generic error class for this module."""

class UnrecognizedCharacter(Error):
  """Position `pos` in the text doesn't match any tokens."""
  def __init__(self, string, start, stop=None):
    self.value = (string, start, stop)
    self.char = string[start:stop]
    self.span = span_of(string, start, stop)

  def __str__(self):
    return "%s: couldn't match %r" % (self.span, self.char)


class Token(object):
  """A token matched in a string."""
  def __init__(self, m):
    self.value = m.group()
    self.start, self.end = m.span()
    self.span = (self.start, self.end)
    self.pos = m.pos
    self.token = m.lastgroup
    self.string = m.string

  def __repr__(self):
    return 'Token(%r)' % str(self)

  def __str__(self):
    return '%s -> %r' % (self.token, self.value)
  

def span_of(string, start, stop):
  """Return a string representing the position of this slice."""
  def column_of(p):
    line_start = string.rfind('\n', 0, p)
    if line_start == -1:  return p
    else:  return p - line_start
  stline, stcol = string.count('\n', 0, start) + 1, column_of(start)
  loc = '%i.%i' % (stline, stcol)
  if stop > start + 1 and string.count('\n', start, stop) > 0:
    col = column_of(stop)
    return loc + '-%i.%i' % (
        stline + string.count('\n', start, stop), col)
  elif stop > start + 1:
    col = column_of(stop)
    return loc + '-%i' % (col)
  else:
    return loc

class Scan(object):
  """A scanner for a particular set of tokens (defined as keyword args)."""
  def __init__(self, **tokens):
    self.tokens = tokens
    self.__compile()
    self.ignores = set()

  def __call__(self, *args, **opts):
    """Call on a string (or a list of strings) to generate tokens."""
    # Start at the beginning of this text.
    text, pos = ''.join(args), 0
    while pos < len(text):
      # Match the text, looking for the next token.
      m = self.regex.match(text, pos)
      if m is None:
        # No token was found, raise an error.
        raise UnrecognizedCharacter(text, pos, pos + 1)
      elif m.lastgroup in self.ignores:
        # An ignored token was found, continue without yielding.
        pos = m.end()
        continue
      else:
        # Found a token; yield its name and the text it matched.
        yield Token(m)
        pos = m.end()

  def __str__(self):
    return '\n'.join('%s -> %s' % (k, v) for (k, v) in self.tokens.items())

  def __compile(self):
    """Compile the dict of tokens into a regular expression."""
    self.regex = re.compile('|'.join(
      '(?P<%s>%s)' % (k, self.tokens[k]) for k in self.tokens))

  def update(self, **tokens):
    """Update the tokens matched with token=regex pairs."""
    self.tokens.update(tokens)
    self.__compile()
  
  def ignore(self, key):
    """Ignore a particular token when it is found."""
    self.ignores.add(key)

  def unignore(self, key):
    """Remove a token from the ignores list."""
    self.ignores.discard(key)


if __name__ == '__main__':
  import doctest
  doctest.testmod()
