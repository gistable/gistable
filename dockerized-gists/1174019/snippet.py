import mock

def returnList(items):
  def func():
    for item in items:
      yield item
    yield mock.DEFAULT

  generator = func()

  def effect(*args, **kwargs):
    return generator.next()

  return effect


m = mock.Mock()
m.side_effect = returnList([1,2,3])
for i in ['a', 'b', 'c']:
    print i, m()
