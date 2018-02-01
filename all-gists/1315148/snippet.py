# -*- coding: utf-8 -*-

# Dead simple BEMHTML renderer concept via PyV8 (code.google.com/p/pyv8/)

import os
import PyV8

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(PROJECT_ROOT, 'pages/page')

ctxt = PyV8.JSContext()
ctxt.enter()

bemjson = open(os.path.join(PAGE, 'example.bemjson.js'))
bemhtml = open(os.path.join(PAGE, 'example.bemhtml.js'))

# Evaluting bemhtml.js template
ctxt.eval(bemhtml.read())

# `json.dumps`?
html = ctxt.eval("BEMHTML.apply(" + bemjson.read() + ")")

print html
