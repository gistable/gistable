import sys

def exec_(code, globals, locals):
  if sys.version_info >= (3, 0):
    exec(code, globals, locals)
  else:
    exec("exec code in globals, locals")