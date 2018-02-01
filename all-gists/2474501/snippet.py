class attrdict(defaultdict):
    def __getattr__(self, key): return self[key]
    def __setattr__(self, key, val): self[key]=val

def tree(): return attrdict(tree)