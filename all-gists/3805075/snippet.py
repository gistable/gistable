main = lambda port:  (lambda dt: (lambda mm:  (lambda n: (map(lambda r:  (lambda 
    rr: setattr(n, *rr) if (type(rr) is tuple and len(rr) == 2) else None)(r()), 
    [lambda: map(setattr, *zip(*[(n, m, __import__(m)) for m in mm.m.decode('ba'
    'se64').split()])), lambda: map(n.s['signal.signal'], (n.s['signal.SIGINT'], 
    n.s['signal.SIGTERM']),  [lambda s, f: (n.s['sys.exit']() if n.f else [n.sa(
    mm.l[0], n.o)]  and n.u('f', True)  or n.fc(n.l))] * 2), lambda: setattr(mm, 
    'l', mm.l.decode('base64').split('~~~')), lambda: ('sw', n.s['types.Functio'
    'nType'] (compile("try:\n\tv = n.select.select(n.so, n.w(), [])\nexcept n.s"
    "elect.error, e:\n\tif e[0] != n.errno.EINTR: raise\nelse:\n\tn.u('sr', v)", 
    '', 'exec'), dict(n=n, OSError=OSError))),lambda: ('l', n.s['socket.socket']
    (n.s['socket.AF_INET'], n.s['socket.SOCK_STREAM'])), lambda: n.s['l.bind']((
    '', port)), lambda: n.s['l.listen'](5), lambda: ('ro', lambda: filter(lambda 
    s: s in n.nn,  n.so)),  lambda: n.update(si=(lambda o: o.__setitem__),  di=(
    lambda o: o.__delitem__),  cr=n.s['re.compile'](mm.l[11]), nn={},  dp=lambda 
    s, d, c, l: n.dd.get(c, d)(s, l, c), dd=dict(me=lambda s, l, c: n.sa(mm.l[14
    ] % (n.nn[s], l)), quit=lambda s, l, c: n.c(s),  who=lambda s, l, c: n.ws(s, 
    mm.l[1] + ', '.join(n.s['nn.values']())), help=lambda s, l, c: n.ws(s, mm.l[
    2]), nick=lambda s, l, c: ((([n.sa(mm.l[3] % (n.nn[s], l))] and n.si(n.nn)(
    s, l))  if n.nr.match(l)  else  n.ws(s, mm.l[4]))  if l not in n.nn.values() 
    else n.ws(s, mm.l[7]))), so=(n.u('f', False) or [n.l]), ib=n.s['collections'
    '.defaultdict'](list),  ob=n.s['collections.defaultdict'](list),  o=(lambda: 
    filter(lambda s:  s is not n.l, n.so)),  w=(lambda: filter(n.ob.__getitem__, 
    n.o())), ws=(lambda s, l: n.ob[s].append(l + '\r\n')), nr=n.s['re.compile'](
    mm.l[12]),  sa=(lambda d, f=n.ro: map(lambda s: n.ws(s, d), f())), fs=set(), 
    c=(lambda s: [n.sa(mm.l[13] % n.nn[s])  if s in n.nn and s not in n.fs  else 
    None] and n.s['fs.add'](s)),  fc=(lambda s:  [s.close()] and (n.so.remove(s) 
    if s in n.so else None) or (n.fs.remove(s) if s in n.fs else None) or (n.di(
    n.ib)(s) if s in n.ib else None)  or  (n.di(n.ob)(s) if s in n.ob else None) 
    or (n.di(n.nn)(s)  if s in n.nn else  None))),  lambda:  map(lambda f:  map(
    apply, [lambda: n.u('sr', ([], [], [])),  lambda: n.sw(), lambda: map(apply, 
    [lambda *ss: map(lambda s: map(apply,  [lambda: n.sa(mm.l[8]), lambda: n.so.
    append(s.accept()[0]),  lambda: n.ws(n.so[-1], mm.l[6])])  if s is n.l  else 
    map(apply,  [lambda: n.ib[s].append(s.recv(4096)) or  (n.c(s) if n.ib[s][-1] 
    == '' else None)]), ss), lambda *ss: map(lambda s: (lambda d: (n.si(n.ob)(s, 
    [d[s.send(d):]])  or  (n.si(n.ob)(s, []) if n.ob[s] == [''] else None)))(''.
    join(n.ob[s])), ss),  lambda *ss: None], n.sr), lambda: [n.di(v)(slice(None, 
    None)) for k, v in n.ob.items() if v and not filter(None, v)],  lambda: n.u(
    'sl', {}), lambda: map((lambda (k, v): n.si(n.sl)(k, ''.join(v).split('\r\n'
    )) or n.si(n.ib)(k, [n.sl[k].pop()])), n.ib.items()),  lambda: n.sl and map(
    lambda (s, l): ((n.sa(mm.l[15] %  (n.nn[s], l[1:] if l.startswith('//') else 
    l))  if not l.startswith('/')  or l.startswith('//') else (n.dp(s, lambda s, 
    l, c:  n.ws(s, mm.l[9] % c),  *n.s['cr.match'](l).groups())))  if  s in n.nn 
    else (((n.si(n.nn)(s, l) or [n.ws(s, mm.l[5])] and n.sa(mm.l[10] % l)) if n.
    nr.match(l)  else n.ws(s, mm.l[4]))  if l not in n.nn.values()  else n.ws(s, 
    mm.l[7]))),  [(s, l.rstrip())  for s, ll  in  n.sl.items()  for l  in  ll]), 
    lambda: n.f and map(lambda (s, b): n.fc(s) if not filter(None, b) else None,
    n.ob.items()), lambda:  map(lambda s:  n.fc(s) if not filter(None,  n.ob[s]) 
    else None, list(n.fs))]), iter(lambda: bool(n.so), False)), lambda: n.s['l.'
    'close']()])))(dt()))(dt(m='c3lzIHNpZ25hbCBzb2NrZXQgc2VsZWN0IGNvbGxlY3Rpb25'
    'zIGVycm5vIHR5cGVzIGl0ZXJ0b29scyByZQ==', l='KioqIFNlcnZlciBnb2luZyBkb3duIX5'
    '+fioqKiBDdXJyZW50bHkgY29ubmVjdGVkOiB+fn4qKiogQXZhaWxhYmxlIGNvbW1hbmRzOg0KK'
    'ioqICAvaGVscCAtLSBnZXQgaGVscA0KKioqICAvcXVpdCAtLSBkaXNjb25uZWN0DQoqKiogIC9'
    'tZSAtLSBwZXJmb3JtIGFuIGFjdGlvbg0KKioqICAvd2hvIC0tIGxpc3QgY29ubmVjdGVkIHVzZ'
    'XJzDQoqKiogIC9uaWNrIC0tIGNoYW5nZSB5b3VyIG5pY2tuYW1lIHRvIHNvbWV0aGluZyBiZXR'
    '0ZXJ+fn4qKiogJXMgaXMgbm93IGtub3duIGFzICVzLn5+fioqKiBUaGF0IG5pY2tuYW1lIGlzI'
    'GludmFsaWQufn5+KioqIFR5cGUgIi9oZWxwIiBmb3IgaGVscC5+fn4qKiogSGVsbG8hIFdoYXQ'
    'gaXMgeW91ciBuaWNrbmFtZT9+fn4qKiogVGhhdCBuaWNrbmFtZSBpcyBhbHJlYWR5IGluIHVzZ'
    'S5+fn4qKiogSW5jb21pbmcgY29ubmVjdGlvbiF+fn4qKiogTm8gc3VjaCBjb21tYW5kOiAvJXN'
    '+fn4qKiogJXMgaGFzIGpvaW5lZC5+fn5eLyhbQS16XSopXHMqKC4qKSR+fn5eW0EtejAtOV9dK'
    'yR+fn4qKiogJXMgaGFzIGxlZnQufn5+KiAlcyAlc35+fjwlcz4gJXM=')))(type('', (dict,
    ), dict(__getattr__=lambda s, k:  s[k],  u=lambda s, *a:  s.__setitem__(*a),
    __setattr__=lambda s, k, v: s.__setitem__(k, v),  s=property(lambda s: type(
    '', (object,),  dict(__getitem__=lambda ss, k: reduce(getattr, k.split('.'), 
    s)))()))))