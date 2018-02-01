from __future__ import with_statement
import inspect

class Test(object):
  def __init__(self, name):
    self.name = name
  
  def __enter__(self):
    return self
  
  def __exit__(self, type, value, traceback):
    locals = inspect.getouterframes(inspect.currentframe())[1][0].f_locals
    
    print "BEFORE: %s" % (self.name)
    if locals.has_key('before') and inspect.isfunction(locals['before']):
      locals['before']()
      locals['before'] = None
    
    for l in locals:
      if inspect.isfunction(locals[l]) and l.startswith("it_"):
        locals[l]()
        locals[l] = None
    
    print "AFTER: %s" % (self.name)
    if locals.has_key('after') and inspect.isfunction(locals['after']):
      locals['after']()
      locals['after'] = None

with Test("Proof of concept") as t:
  def before():
    global create_me
    create_me = "- set in the before, and globally available"

  def it_sets_the_variable():
    global create_me
    print create_me  

with Test("Adding a custom before and after") as t:
  def before():
    print "CUSTOM BEFORE"
  
  def after():
    print "CUSTOM AFTER"
    
  def it_prints_anything():
    print "- i am a lonely print statement"