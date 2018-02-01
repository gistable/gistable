#!/usr/bin/env python
"""
Compile Django Templates from the command line

Thomas Parslow 2014
tom@almostobsolete.net
tomparslow.co.uk almostobsolete.net

Run passing in the the template file to read and the context data as
JSON. Will output the compiled HTML on stdout.

python dango-template.py mytemplate.html '{"context_var": "value"}'
"""
from django.template import Template, Context
from django.template.loader import get_template
from django.conf import settings
import sys
import os
import codecs
import json
import argparse

parser = argparse.ArgumentParser(description='Compile a Django template')
parser.add_argument('--path', type=str, nargs='*',
                   help='Path to look for templates for {%% include %%} and {%% extends %%}')
parser.add_argument('template', type=str,
                   help='File of template to process (eg mytemplate.html)')
parser.add_argument('context', type=str, nargs="?",
                   help="""Content data in JSON format (eg '{"var": "value"}')""")

args = parser.parse_args()

settings.configure(
# Default template dir is current working directory if not specified via --path
    TEMPLATE_DIRS=args.path or [os.getcwd()]
)


template = get_template(args.template)
c = Context(json.loads(args.context) if args.context else {})
print template.render(c)
