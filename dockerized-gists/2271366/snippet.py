def head(l):
    return l[0]

def tail(l):
    return l[1:]

def is_not_in_tail(h, l):
    if h in tail(l):
        return False
    return True

def remove_head(h, l):
    if h is head(l):
        l.remove(h)
    return l

def merge(list_of_linearization):
    for l in list_of_linearization:
        h = head(l)
        if all(is_not_in_tail(h, l) for l in list_of_linearization):
            list_of_stripped = [remove_head(h, l) for l in list_of_linearization]
            list_of_stripped = [i for i in list_of_stripped if len(i) != 0]
            if len(list_of_stripped) == 0:
                return [h]
            return [h] + merge(list_of_stripped)
    raise TypeError("Cannot create a consostent method resolution")

def c3_algo(C):
    if C is object:
        return [object]

    bases = list(C.__bases__)
    return [C] + merge([c3_algo(b) for b in bases] + [bases])

# class F(): pass
# class E(): pass
# class D(): pass
# class C(D,F): pass
# class B(D,E): pass
# class A(B,C): pass
class F(): pass
class E(F): pass
class G(F,E): pass