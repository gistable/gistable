#!/usr/bin/python
import ast, _ast, os

for root, dirs, files in os.walk('.'):
  for name in files:
    if name.endswith('.py'):
      full = os.path.join(root, name)
      t = ast.parse(open(full).read())
      for n in ast.walk(t):
        if isinstance(n, _ast.Str) and not isinstance(n.s, unicode):
          if any(ord(c) > 127 for c in n.s.decode('utf-8')):
            print full, 'line', n.lineno, 'col', n.col_offset, ':', n.s.decode('utf-8')
