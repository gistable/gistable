>>> e = codecs.lookup('zlib').incrementalencoder()
>>> e.encode('foo')
'x\x9c'
>>> e.encode('bar')
''
>>> e.encode('baz')
''
>>> e.encode('', final=True)
'K\xcb\xcfOJ,JJ\xac\x02\x00\x12{\x03\xb7'