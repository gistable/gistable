class Test(object):
  @property
  def x(self):
    print "property-x"
    return 7

  def y(self):
    return 8

  a = 9

  def __getattr__(self, name):
    print "getattr:", name
    #if isinstance(getattr(self.__class__, name, None), property):
    #  return super(Test, self).__getattr__(name)
    return 1
