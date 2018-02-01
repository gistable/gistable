#!/usr/bin/python
# -*-coding: utf-8 -*-

import re 

string = "aaaeijfdfsafdo"

Resultado= re.sub("^aa.+o$", "u", string)

print Resultado