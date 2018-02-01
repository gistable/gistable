'''
Copyright (c) 2013 Zohaib Sibte Hassan
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import sqlite3
import json
import msgpack
import cPickle

class BaseAdapter(object):
  def dumps(self, doc):
    raise Exception('Not implemented')

  def loads(self, st):
    raise Exception('Not implemented')

  def doc_value_of(self, doc, key):
    d = self.loads(doc)
    return d[key]

  def __is_sub_dict(self, d, q):
    for k, q_val in q.items():
      key_path = k.split('.')
      d_val = d
      for i in key_path:
        if not i in d_val:
          return False
        d_val = d_val[i]
      if q_val != d_val:
        return False
    return True

  def doc_matches(self, doc, query):
    try:
      q = self.loads(query)
      d = self.loads(doc)
      return self.__is_sub_dict(d, q)
    except Exception as e:
      print e
   
  def cursor(self, csr):
    return self.Cursor(csr, self)

  class Cursor(object):
    def __init__(self, cursor, adapter):
      self.crsr = cursor
      self.adapter = adapter

    def __iter__(self):
      r = self.crsr.fetchone()
      while r:
        d = self.adapter.loads(r['document'])
        if '_id' not in d:
          d['_id'] = r['id']
        yield d
        r = self.crsr.fetchone()

      self.crsr.close()

    def all(self):
      ret = []
      for d in self:
        ret.append(d)
      return ret

class JSONAdapter(BaseAdapter):
  def dumps(self, doc):
    return buffer(json.dumps(doc))

  def loads(self, b):
    return json.loads(str(b))

class MsgPackAdapter(BaseAdapter):
  def dumps(self, doc):
    return buffer(msgpack.packb(doc))

  def loads(self, b):
    return msgpack.unpackb(b)

class PickleAdapter(BaseAdapter):
  def dumps(self, d):
    return buffer(cPickle.dumps(d))

  def loads(self, s):
    return cPickle.loads(str(s))

class NSQlite3(object):

  def __init__(self, file_name, storage_adapter=JSONAdapter()):
    self.__db = sqlite3.connect(file_name)
    self.__db.row_factory = sqlite3.Row
    self.__adapter = storage_adapter
    self.__db.create_function('doc_value_of', 2, self.__adapter.doc_value_of)
    self.__db.create_function('doc_matches', 2, self.__adapter.doc_matches)

  def collection(self, name):
    return Collection(self.__db, name, self.__adapter)

class Collection(object):
  def __init__(self, connection, name, storage_adapter):
    self.name = name
    self.db = connection
    self.__adapter = storage_adapter
    self.create()

  def create(self):
    c = self.db.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.name,))
    r = c.fetchone()
    if not r or r['name'] != self.name:
      ret = c.execute("CREATE TABLE %s ( id INTEGER PRIMARY KEY AUTOINCREMENT, document BLOB )" % (self.name))
    c.close()
    return self

  def drop(self):
    c = self.db.cursor()
    c.execute("DROP TABLE %s" % (self.name))
    c.close()
    return self

  def ensure_index(self):
    #For future indexing
    pass

  def insert(self, doc):
    c = self.db.cursor()
    ret = {}
    ret.update(doc)
    c.execute("INSERT INTO %s(document) VALUES(?)" % (self.name), [self.__adapter.dumps(ret)] )
    #TODO: Update indexes
    self.db.commit()
    did = c.lastrowid
    return ret

  def delete(self, query):
    c = self.db.cursor()
    c.execute("DELETE FROM %s WHERE doc_matches(document, ?)" % (self.name), [self.__adapter.dumps(query)])
    r = c.rowcount
    c.close()
    self.db.commit()
    return r

  def find(self, query):
    c = self.db.cursor()
    c.execute("SELECT id, document FROM %s WHERE doc_matches(document, ?)" % (self.name), [self.__adapter.dumps(query)])
    return self.__adapter.cursor(c)

def main_test():
  lite = NSQlite3('boo.sqlite3', MsgPackAdapter())
  coll = lite.collection('foo')

  coll.insert({'foo': 'bar', 'say': True, 'name': {'first': 'Zohaib', 'last': 'Hassan'}})
  coll.insert({'foo': 'bar2'})
  coll.insert({'foo': 'bar', 'int': 120})

  print "Finding existing....", coll.find({'name.first': 'Zohaib'}).all()
  print "........"
  print "Finding not existing...", coll.find({'foo': 'ex'}).all()

  print "Deleting..."
  coll.delete({})

if __name__ == "__main__":
  main_test()
