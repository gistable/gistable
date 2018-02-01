# taken from here: http://web.archive.org/web/20110527163743/https://svn.enthought.com/enthought/browser/sandbox/docs/coding_standard.py

""" This module is an example of the Enthought Python coding standards.

It was adapted from the Python Enhancement Proposal 8 (aka PEP 8) titled
'Style Guide for Python Code' (http://www.python.org/peps/pep-0008.html).

The first item in a module must be a documentation string (docstring).  The
first line of the docstring should be a one line summary.  If a more
detailed description is required, put an empty line before it.

Package names are lowercase with an underscore to separate each word and are
ALWAYS singular:-

e.g.

    widget
    event_handler

Module names are lowercase with an underscore to separate each word.

e.g.

    coding_standard.py
    my_class.py


Module Length
-------------
A python module should under normal circumstances be no longer than 500 lines
of code *including* comments (and even that's pushing it!).  There are certain
mitigating circumstances such as modules containing a collection of related
library functions, but even then, think about any possible logical groupings
and split them up accordingly.

"""

# Indentation
# -----------
# Each indentation level should be 4 spaces.  Code should always be indented
# with spaces only.  Code indented with a mixture of tabs and spaces should be
# converted to using spaces exclusively (In Emacs, make sure that
# 'indent-tabs-mode' is nil, or select the whole buffer and hit
# ESC-x untabify).  When invoking the python command line interpreter with the
# -t option, it issues warnings about code that illegally mixes tabs and
# spaces.  When using -tt these warnings become errors.  These options are
# highly recommended!

# Line length
# -----------
# Lines must not exceed 79 characters in length (in deference to Emacs users...
# ... as Emacs wraps on the 80th column).
#
# The preferred way of wrapping long lines is by using Python's implied line
# continuation inside parentheses, brackets and braces. If necessary, you can
# add an extra pair of parentheses around an expression, but somtimes using a
# backslash looks better.  Make sure to indent the continued line
# appropriately.  Emacs Python-mode does this right.


# Import Statements
# -----------------
# Import statements are always put at the top of the file, just after any
# module comments and docstrings, and before any module globals and constants.
#
# Imports should be grouped and ordered as follows:-
#
# 1. Standard library imports
# 2. Related major package imports (i.e. all email package imports next).
# 3. Application specific imports.
# 4. Local imports (ie. local to the current package).
#
# You should put a blank line between each group of imports.
#
# Relative imports for intra-package imports are highly discouraged.  Always
# use the absolute package path for all imports.
#
# Imports should be USUALLY be on separate lines:-

# Standard library imports.
import os
import sys

# Although it is okay to say this:-
from types import StringType, ListType

# And I think this looks OK to as long as it doesn't turn into a list
# of more than ~5.
import os, sys

# Major packages.
import wx
import chaco

# Application specific imports.
from baz import Baz

# Local imports.
from local import Local

# The following form of the import statement should be used with EXTREME
# caution, and only when importing names from a large and fundemental package
# such as Numeric or scipy, and even then, only when there are a large number
# of names being imported (for example, do not use 'from Numeric import *' if
# 'from Numeric import array will do ;^).
from mypackage import *

# Comments
# --------
#
# Comments are a great.  Learn to write good comments.  Or else!  Comments that
# contradict the code are worse than no comments.  Always make a priority of
# keeping the comments up-to-date when the code changes!
#
# Comments should be complete sentences.  If a comment is a phrase or
# sentence, its first word should be capitalized, unless it is an identifier
# that begins with a lower case letter (never alter the case of identifiers!).
#
# Block comments generally consist of one or more paragraphs built out of
# complete sentences, and each sentence should end in a period.
#
# You should use two spaces after a sentence-ending period, since it makes
# Emacs wrapping and filling work consistently.
#
# When writing English, Strunk and White apply.

# Docstrings
# ----------
#
# The first line of a docstring should be a one line summary. As noted in the
# example below.  Follow that line with a blank line, and then continue with a
# description or examples as appropriate.  Examples are called out on a new
# line, indented an additional four spaces, and begin with >>>.
# This convention will produce nicely formated examples in the resulting html
#  pages, so do not hesitate to use it.  Conventions for writing good
# docstrings are found in PEP 257 (http://www.python.org/peps/pep-0257.html).

def my_function(x, y, z):
    """ A function definition must contain a docstring.

    Function names are lowercase with an underscore used to separate each word.

    """

    # Block comments generally apply to some (or all) code that follows them,
    # and are indented to the same level as that code.  Each line of a block
    # comment starts with a # and a single space (unless it is indented text
    # inside the comment).
    #
    # Paragraphs inside a block comment are separated by a line.
    s = x + y + z

    # An inline comment is a comment on the same line as a statement.
    # Inline comments should be used SPARINGLY.  Inline comments should be
    # separated by at least two spaces from the statement.  They should start
    # with a # and a single space.
    #
    # Remember to use SPARINGLY, although sometimes, they can be useful:-
    s = s + 1    # Compensate for the border.

    return s


class FooBar(Baz):
    """ A class definition must contain a docstring.

    As always the first line of the docstring must be a one line summary.

    Class names are CamelCase.

    """
    # Both traits and methods should be grouped by the 'role' or 'interface'
    # that they are part of.  This is the syntax that I use to mark them.

    #### 'Baz' interface #####################################################

    # ALL traits must be commented.
    name = Str

    # Non-public traits (ie. those intended to be either 'protected' or
    # private) should be preceded by single or double underscores as for
    # ordinary Python attributes).

    #### Protected interface ##################################################

    _a_non_public_trait = Dict

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    # 'Special' methods (ie. those methods starting and ending in double
    # underscores) should usually be grouped at the start of the class
    # definition.  The exception is when the class is implementing the
    # interface of a built-in type such as 'list' or 'dict'.  In that case
    # the special methods on the interface follow the rules listed below.
    def __init__(self):
        """ Creates a new Foo. """

        # Attribute names are lowercase with an underscore used to separate
        # each word.
        self.public_attribute = 1

        # A non-public attribute starts with a single underscore.  This does
        # not enforce any limitation on the attribute's use, but it shows that
        # the attribute is intended for use only by this class and any derived
        # classes.
        self._non_public_attribute = "Hi there"

        # A private attribute starts with a double underscore.  Python will
        # mangle such names so that they are invisible outside of the class.
        #
        # Well, actually you can get to them if you try hard enough - although
        # to save time just clear your desk and have security escort you out of
        # the building.  Its been great working with you ;^).
        self.__private_attribute = 42

        # Functions/methods that do not return a value should still be
        # delimited by a return statement.  Please tell me you don't have to
        # ask why!
        return

    # Methods should be grouped and ordered as follows:-
    #
    # 1) 'object interface (ie. special methods).
    # 2) Methods offered on inherited or delegated interfaces of the class.
    # 3) Methods offered on the primary public interface of the class.
    # 4) Non-public methods.
    # 5) Private methods.

    ###########################################################################
    # 'Baz' interface.
    ###########################################################################

    def an_overridden_bar_method(self):
        """ A method definition must contain a docstring.

        Method names are lowercase with an underscore used to separate each
        word.

        The ONLY exception to this is if you are inherting from a 3rd-party
        class that uses a different naming convention (eg. wxPython
        uses CamelCase method names).  In that case you must follow the same
        style as the 3rd-party class (assuming it is consistent of course ;^).

        """

        pass

    ###########################################################################
    # 'FooBar' interface.
    ###########################################################################

    def my_function(self, x, y, z):
        """ A method definition must contain a docstring. """

        return x + y + z

    ###########################################################################
    # Protected interface.
    ###########################################################################

    def _non_public_method(self):
        """ A non-public method starts with a single underscore.

        This does not enforce any limitation on the method's use, but it
        shows that it is intended for use only by this class and any derived
        classes.

        """

        pass

    ###########################################################################
    # Private interface.
    ###########################################################################

    def __private_method(self):
        """ A private method starts with a double underscore.

        Python will mangle such names so that they are invisible outside of
        the class.

        Well, actually you can get to them if you try hard enough - although
        to save time just clear your desk and have security escort you out of
        the building.  Its been great working with you ;^).

        """

        pass


# Exceptions
# ----------
#
# Always use class exceptions instead of the old-style string exceptions.
class MessageError(Exception):
    """ Base class for errors in the email package.

    Exceptions are classes too! Hence exception names are CamelCase.

    """
    
    pass


# Whitespace in Expressions and Statements
def example():
    """ How to use whitespace in expressions and statements. """

    # Around brackets, parentheses and braces:-
    #
    # BAD
    spam( ham[ 1 ], { eggs: 2 } )

    # GOOD
    spam(ham[1], {eggs : 2})

    # Around a comma, semicolon, or colon, as in (although multi-statement
    # lines are STRONGLY discouraged!):-
    #
    # BAD
    if x == 4 : print x , y ; x , y = y , x

    # GOOD
    if x == 4: print x, y; x, y = y, x

    # Function/method calls.
    #
    # BAD
    spam (1)

    # GOOD
    spam(1)

    # Indexing/slicing.
    #
    # BAD
    dict ['key'] = list [index]

    # GOOD
    dict['key'] = list[index]

    # Groups of assignment statements.
    #
    # BAD
    x             = 1
    y             = 2
    long_variable = 3

    # GOOD
    x = 1
    y = 2
    long_variable = 3

    # These binary operators should aways surrounded with a single space.
    #
    # assignment (=), comparisons (==, <, >, !=, <>, <=, >=, in, not in, is,
    # is not), Booleans (and, or, not).

    # Use your better judgment for the insertion of spaces around arithmetic
    # operators.  Always be consistent about whitespace on either side of a
    # binary operator.
    #
    # Some examples:
    i = i+1
    submitted = submitted + 1
    x = x*2 - 1
    hypot2 = x*x + y*y
    c = (a+b) * (a-b)
    c = (a + b) * (a - b)

    return


# Don't use spaces around the '=' sign when used to indicate a keyword
# argument or a default parameter value.  For instance:
def complex(real, imag=0.0):
    return magic(r=real, i=imag)

#### EOF ######################################################################