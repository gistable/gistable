>>> sample = {"a":2,"b":{"c":44}}
>>> sample.get("b",{}).get("c")    # is gross
>>> 
>>> class nestdict(dict):
...   def __floordiv__(self, k):
...     v = self.get(k)
...     if isinstance(v, dict): return nestdict(v)
...     return v
... 
>>> z = nestdict(sample)
>>> z // "a"
2
>>> z  // "b"
{'c': 44}
>>> z // "b" // "c"
44
>>> 
