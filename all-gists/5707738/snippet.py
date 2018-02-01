#!/usr/bin/env python

import re

pattern = '.*<(iframe|param).*(src|value)="(?P<link>http://www.youtube.com/(embed|v)/[a-zA-Z0-9/\.\?&;=\+_-]+);?.*".*>.*</(iframe|param)>.*'

action = re.compile(pattern)
result = action.findall('<div><iframe.....></iframe><param......></param></div>')

print result