from riak import RiakError

class Bucket(object):
  """Wrap up retries and conflict resolution"""
  def __init__(self, client, name, resolve, retries=5):
    self.client = client
    self.name = name
    self.bucket = client.bucket(name)  # base bucket
    self.resolve = resolve
    self.retries = retries
    
  def get(self, key):
    """Get resolved key"""
    tries = self.retries
    while tries:
      try:
        obj = self.bucket.get(key)
        if not obj.has_siblings():
          return obj.get_data()
        resolved_data = self.resolve([s.get_data() for s in obj.get_siblings()])
        first_obj = obj.get_sibling(0)  # magically sets the right vclock
        first_obj.set_data(resolved_data)
        first_obj.store()
        return first_obj.get_data()
      except RiakError, e:
        pass
      tries -= 1
    raise e

  def modify(self, key, modify_data):
    """Modify key"""
    tries = self.retries
    while tries:
      try:
        obj = self.bucket.get(key)
        data = None
        if not obj.has_siblings():
          data = obj.get_data()
        else:
          print obj.get_sibling_count(), obj.vclock()
          raise Exception()
          data = self.resolve([s.get_data() for s in obj.get_siblings()])
        first_obj = obj.has_siblings() and obj.get_sibling(0) or obj
        first_obj.set_data(modify_data(data))
        first_obj.store()
        return first_obj.get_data()
        return True
      except RiakError, e:
        pass
      tries -= 1
    raise e

# semi-useless example
def resolve_random(siblings):
  """Super simple resolver, pick a random one!"""
  return random.sample(siblings, 1)[0]

# semi-useful example of a naive 1:30am increment only distributed counter
def count_resolve(siblings):
  """collapse sibling steps into one"""
  first = siblings.pop()
  for s in siblings:
    if s is not None:  # ?
      # all siblings ought to have the same 'last'
      # assert first['last'] == s['last']
      first['step'] += s['step']
  return first

def count_modify(incr=1):
  """collapse previous state into last, add current increment as step"""
  def _mod(prev):
    if prev is None:
      prev = {'last': 0, 'step': 0}
    return {'last': prev['last'] + prev['step'], 'step': incr}
  return _mod

def main():
  import riak

  client = riak.RiakClient(port=8091)
  old_bucket = client.bucket('counters')
  old_bucket.set_allow_multiples(True)
  obj = old_bucket.get('foo')
  obj.delete()
  obj.reload()
  assert obj.get_data() is None
  assert obj.exists() == False

  bucket = Bucket(client, 'counters', count_resolve, retries=5)
  assert bucket.get('foo') is None
  assert bucket.modify('foo', count_modify(1)) == {'step': 1, 'last': 0}
  assert bucket.get('foo') == {'step': 1, 'last': 0}

  # create a bunch of siblings
  obj1 = riak.RiakClient(port=8091).bucket('counters').get('foo')
  obj2 = riak.RiakClient(port=8091).bucket('counters').get('foo')
  obj3 = riak.RiakClient(port=8091).bucket('counters').get('foo')

  obj1.set_data({'last': 1, 'step': 1}).store()   # +1
  obj2.set_data({'last': 1, 'step': 99}).store()  # +99
  obj3.set_data({'last': 1, 'step': 7}).store()   # +7

  obj.reload()
  assert obj.has_siblings()
  assert obj.get_sibling_count() == 3

  assert bucket.get('foo') == {'step': 107, 'last': 1}

  obj5 = riak.RiakClient(port=8091).bucket('counters').get('foo')
  assert obj5.has_siblings() == False
  assert obj5.get_data() == {'step': 107, 'last': 1}

if __name__ == '__main__':
  main()
