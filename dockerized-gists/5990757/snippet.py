##
## Pairing heap data structure
## More information on wiki:
## http://en.wikipedia.org/wiki/Pairing_heap
## 
## Data types
## Heap :: (Elem | None, Subs)
## Subs :: None | (Heap, Subs)
##

def heap(el=None):
    return (el, None)

def insert(h, el):
    return meld(h, heap(el))

def extract((_, subs)):
    return pairing(subs)

def min((el, subs)):
    return el

def meld((el1, subs1), (el2, subs2)):
    if el1 is None: return (el2, subs2)
    if el2 is None: return (el1, subs1)
    if el1 < el2:
        return (el1, ((el2, subs2), subs1))
    else:
        return (el2, ((el1, subs1), subs2))

def pairing(qs):
    if qs is None: return heap()
    (q1,tail) = qs
    if tail is None: return q1
    (q2, tail) = tail
    return pairing((meld(q1,q2), tail))


if __name__ == "__main__":
    print "=== Pairing heap ==="

    from random import randint

    ph = heap()
    for _ in xrange(20):
        ph = insert(ph, randint(1,20))

    # emulate heapsort
    while 1:
        if min(ph) is None: break
        print "->", min(ph)
        ph = extract(ph)