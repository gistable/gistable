#!/usr/bin/python
class List(list):
    def dup(self):
        def _dup(lst,ancestors):
            for orig,copy in ancestors:
                if lst == orig:
                    return copy
            copy = lst[:]
            _ancestors = ancestors+[(lst,copy)]
            for i,x in enumerate(copy):
                if isinstance(x, list):
                    copy[i] = _dup(x, _ancestors)
            return copy
        return List(_dup(self, []))

    def mapped(self,proc):
        return List(map(proc,self))

    def map(self,proc):
        self[:] = map(proc,self)
        return self

    def filtered(self,proc):
        return List(filter(proc,self))

    def filter(self,proc): 
        self[:] = filter(proc,self)
        return self

    def remove_if(self,proc): 
        return self.filter(lambda x: not proc(x))

    def remove_all(self,val): 
        return self.remove_if(lambda x:x==val)

    def compacted(self):
        return self.filtered(lambda x:x!=None)

    def compact(self):
        return self.remove_every(None)
   
    def uniqed(self):
        dummy = List()
        for x in self:
            if x not in dummy: 
                dummy.append(x)
        return dummy
    
    def uniq(self):
        self[:] = self.uniqed()
        return self

    def sorted(self,*args,**kw):
        return List(sorted(self,*args,**kw))

    def sort(self,*args,**kw):
        self[:] = sorted(self,*args,**kw)
        return self

    def reversed(self):
        return List(reversed(self))

    def reverse(self):
        self[:] = reversed(self)
        return self
    
    def flattened(self):
        dummy = List()
        for x in self:
            if isinstance(x,List):
                dummy.extend(x.flattened())
            elif isinstance(x,list):
                dummy.extend(List(x).flattened())
            else:
                dummy.append(x)
        return dummy

    def flatten(self):
        self[:] = self.flattened()
        return self
    
    def concat(self,other):
        self.extend(other)
        return self

    def sliced(self,pos=None,length=None,step=None):
        return List(self[pos:length:step])
        
    def slice(self,pos=None,length=None,step=None):
        self[:] = self[pos:length:step]
        return self

    def unshift(self,val):
        self.insert(0,val)
        return self

    def push(self,val):
        self.append(val)
        return self

    def join(self,d):
        return d.join(self)

    def to_str(self):
        return str(self)

    def reduce(self,*args,**kw):
        proc,arg = args[0],args[1:]
        return reduce(proc,self,*arg,**kw)

    def __getattr__(self,name):
        if name == 'length':
            return len(self)
        else:
            raise AttributeError, "'List' object has no attribute '%s'" % name

    def choose(self,*args,**kw):
        return List(choose(self,*args,**kw))

    def permutation(self):
        return List(permutation(self))

    def combination(self):
        return List(combination(self))

def choose(lst,n,allow_dup=True,distinguish_order=True):
    if allow_dup and distinguish_order:
        next = lambda lst, i: lst
    if allow_dup and not distinguish_order:
        next = lambda lst, i: lst[i:]
    if not allow_dup and not distinguish_order:
        next = lambda lst, i: lst[i+1:]
    if not allow_dup and distinguish_order:
        next = lambda lst, i: lst[:i]+lst[i+1:]

    def _choose(lst,n):
        if n == 0: return [[]]  # from ruby
        #if n == 1: return [[x] for x in lst]
        ans = []
        for i,x in enumerate(lst):
            ans.extend([[x]+l for l in _choose(next(lst,i),n-1)])
        return ans

    return _choose(lst,n)

def permutation(lst,n=None):
    if n == None: n = len(lst)
    return choose(lst,n,allow_dup=False,distinguish_order=True)

def combination(lst,n=None):
    if n == None: n = len(lst)
    return choose(lst,n,allow_dup=False,distinguish_order=False)

def rotation(lst):
    i,ans = 0, []
    while i<len(lst):
        ans.append(lst[i:]+lst[:i])
        i += 1
    return ans
