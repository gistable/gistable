class MyCallable(object):
  def __init__(self, urlparts, callable):
      self.urlparts = urlparts
      self.callable = callable
  def __call__(self, **kwargs):
      print kwargs
      print self.urlparts
  def __getattr__(self, name):
      # Return a callable object of this same type so that you can just keep
      # chaining together calls and just adding that missing attribute to the
      # arguments
      return self.callable(self.urlparts + name, self.callable)

class Service(MyCallable):
  pass

x = Service('a', MyCallable)
x.path.path1()
x.path.path1.path2()