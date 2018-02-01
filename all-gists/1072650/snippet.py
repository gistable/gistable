>>> def agora():
...  return datetime.now()
... 
>>> from ludibrio import Stub
>>> with Stub() as datetime:
...  from datetime import datetime
...  datetime.now() >> 'foo'
... 
>>> agora()
'foo'