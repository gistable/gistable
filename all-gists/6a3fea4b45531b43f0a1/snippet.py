# this is the simplest python program

print "Hello world from Cloud9!"

# click the 'Run' button at the top to start this application


class L(dict):
    """
    Dict like object.  Can be pickled/depickled
    
    """
    def __init__(self):
        print "L __init__ %s"% None
        #self.dict = data

    def __getattr__(self, name):
        print 'L get %s'% name
        return dict.__getitem__(self, name) #.setdefault(name, None)
    
    def __setattr__(self, name, value):
        print 'L set %s = %s'% (name, value)
        dict.__setitem__(self, name, value)

    def __str__(self):
        print 'L str '
        return dict.__str__(self)

    #pickle freindly.
    def __getstate__(self): return self.__dict__
    def __setstate__(self, d): self.__dict__.update(d)
    
a={}
l=L()


from collections import namedtuple

L2 = namedtuple('L2', 'x y'.split())

import pickle

class LW(object):
#    __slots__ = ['data']
    #data={}
    
    def __init__(self, data):
        print "LW __init__ %s"%data
        #object.__init__(self)
        #setattr(self, 'data', data)
        
        # avoid recursion!
        super(LW, self).__setattr__('_data', data)
        #self.data = data
    
    def __getattr__(self, name):
        print 'get / setdefault %s'% name
        if name.startswith('__') and name.endswith('__'):
            return super(LW, self).__getattr__(name)
        if name.startswith('_g'): 
            return super(LW, self).__getattr__(name)
            
        v = self._data.setdefault(name, {})
        if isinstance(v, dict):
            return LW(v)
        return v
        # assume when using this mode, be agressive at setting values
        # if none, it MIGHT be chaining to sub dict
        # lw.a.b = 2
        #return self.dict.setdefault(name, None)
        #return self.dict[name] #.__getitem__(self, name) #.setdefault(name, None)
    
    def __setattribute__(self, name, value):
        print 'setattribute %s = %s'% (name, value)
        self._data[name] = value
        #dict.__setitem__(self, name, value)
    
    def __setattr__(self, name, value):
        print 'setattr %s = %s'% (name, value)
        self._data[name] = value
        #dict.__setitem__(self, name, value)

    def __str__(self):
        print 'L str '
        return str(self._data) #.__str__(self)
        #return str(self.dict)

    #pickle freindly.
    def __getstate__(self): 
        print 'L getstate '
        raise  pickle.PicklingError("Not supported, pickle the dict")
        #return self._data
    def __setstate__(self, d): 
        print 'L setstate '
        raise  pickle.UnpicklingError("Not supported, pickle the dict")
        #ldict = self._data #super(LW, self).__getattr__('_data')
        #ldict.update(d)
        
lw = LW(a)
lw.b = 1
lw.c.x =2
lw.c.z =2
print a, '\n', lw

from pickle import loads, dumps

lwp = dumps(a)
bdash = loads(lwp)


class Meh(object):
    'Replacing a __dict__ with incoming dict seems to work OK.'
    def __init__(self, data):
        self.__dict__ = data
