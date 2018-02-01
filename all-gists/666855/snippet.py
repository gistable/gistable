> s = 'foo bar baz baz'

> reduce(lambda x,y:dict([ (k, (lambda a,b,k:(a[k] + (1 if k in b else 0)))(x,y,k)) for k in x.keys()]+[ (k,1) for k in y.keys() if not k in x ]), map(lambda x: {x:1}, s.split()))

{'bar': 1, 'baz': 2, 'foo': 1}