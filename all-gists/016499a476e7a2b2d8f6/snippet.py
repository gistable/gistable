class A(object):
  def aa(self):
    print 'in A'
    return self.__class__.__name__

class B(A):
  def bb(self):
    print 'in B'
    return super(B, self).aa()    

  def cc(self):
    print 'in B'
    return self.__class__.__name__

>> # tests
>> a = A()
>> a.aa()
in A
'A'
>> b = B()
>> b.aa()  # printed B class, not A
in A
'B'
>> b.bb()
in B
in A
'B'
>> b.cc()
in B
'B'