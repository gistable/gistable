>>> def a(b, c={}):
...     c[b] = b
...     print c
... 
>>> a('prova')
{'prova': 'prova'}
>>> a('gatto')
{'prova': 'prova', 'gatto': 'gatto'}
>>> a('mela')
{'prova': 'prova', 'mela': 'mela', 'gatto': 'gatto'}
