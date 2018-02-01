#!/usr/bin/env python
"""
Highlight stdin using pygments and output to stdout

Re-uses httpie.

Auto-detects the input language.

Will not colorize if piped into something else.

Usage: echo '{"test": "foo", "bar": 123, "bat": false}' | hl
Usage: echo '{"test": "foo", "bar": 123, "bat": false}' | hl | pbcopy (not colored)
"""
import sys
import os
import json
import pygments
import re
from pygments.lexers import *
from pygments import token
from pygments.util import ClassNotFound
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.formatters.terminal import TerminalFormatter
from pygments.formatters.other import NullFormatter
from httpie.pygson import JSONLexer
from httpie import solarized

try:

	FORMATTER = (Terminal256Formatter
	             if '256color' in os.environ.get('TERM', '')
	             else TerminalFormatter)

	if not sys.stdout.isatty():
		FORMATTER = NullFormatter

	formatter = FORMATTER(style=solarized.SolarizedStyle)

	content = sys.stdin.read()

	lexer = guess_lexer(content)

	if isinstance(lexer, MatlabLexer):
		lexer = JSONLexer()

	if isinstance(lexer, JSONLexer):
		content = json.dumps(json.loads(content), indent=4)

	output = pygments.highlight(content, lexer, formatter)

	print output

	sys.exit(0)

except Exception as e:
	sys.exit(-1)
