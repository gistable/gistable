class UF:
    stack = []
    def union(self, p, q):
        self.stack.append([p,q])
        self.merge()
        self.rmDuplicates()
    def merge(self):
        nstack = []
        for bundle in self.stack:
            for num in bundle:
                for bundleo in self.stack:
                    for numo in bundleo:
                        if num == numo:    
                            nstack.append(bundle + bundleo)
        self.stack = nstack
    def connection(self, p, q):
        for bundle in self.stack:
            if p in bundle and q in bundle:
                return True
        return False
    def rmDuplicates(self):
        s = []
        for bundle in self.stack:
            for i in bundle:
                if i not in s:
                    s.append(i)
            bundle = s
            s = []
          

# usage
Machine = UF()
Machine.union(1, 4)
Machine.union(4, 2)
print Machine.connection(1, 2)