# -*- coding: utf-8 -*-
 
def fn(pattrn, table, text, _range):
    x = 0
    if _range[1] <= len(text):
        x = 1
        for i in range(_range[0], _range[1]):
            if text[_range[1] - x] != pattrn[len(pattrn) - x]:
                _ch = text[_range[1] - x]
                r = [x for x in table if x[1] == _ch]
                _shift = len(pattrn) if not r else r[0][0]
                _shift = _range[1] + (_shift + 1 if _shift < 1 else _shift)
                return fn(pattrn, table, text, ((_shift - 1) - (len(pattrn) - 1), _shift))
            x += 1
    return (_range[0], _range[1]) if x > 0 else -1
 
 
def search(pattrn, text):
    text = text.lower()
    m = len(pattrn)
    table = []
    for i in range(0, m):
        tr = [t for t in table if pattrn[m - (i + 1)] == t[1]]
        if not tr:
            table.append((i, pattrn[m - (i + 1)]))
    return fn(pattrn, table, text, (0, len(pattrn)))
       
        
print search(u"paper", u"this paper describes just such a general")

