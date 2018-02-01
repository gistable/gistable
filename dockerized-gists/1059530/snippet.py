# Sick of python dicts not just being object literal syntax? WE* CAN FIX THAT

class objectify(object):
    def __init__(self, d):
        for k in d:
            setattr(self,k,d[k])
    def __repr__(self):
        r = 'objectify({ \n'
        for a in dir(self):
            r += '    '+a+': '
            if a[0:2] == a[-2::] == '__':
                # spesh methods lead to oddball recursion bugs
                r += str(type(getattr(self,a)))+',\n'
            else:
                r += repr(getattr(self,a)) + ',\n'
        r = r[0:-2]+'\n})'
        return r

    def __str__(self):
        r = '{'
        for a in dir(self):
            # str does not include spesh methods
            if not (a[0:2] == a[-2::] == '__'):
                r+=a+': '+repr(getattr(self,a)) +', '
        r = r[0:-2]+'}'
        return r

    # The following three methods give us dict-style get/set
    def __getitem__(self,k):
        return getattr(self,k)

    def __setitem__(self,k,v):
        setattr(self,k,v)

    def __delitem__(self,k):
        delattr(self,k)

# With which we can do something like THIS:

obj = objectify({'a': 1, 'b': lambda x: x+1})

obj.a # == 1
obj.b(1) # == 2

# Hooray! (kind of.)



# * Inspired from a chat with SubStack, though we disagree on how to 'solve the problem' as he would just as soon use dicts as objects in practice.