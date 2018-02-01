#!/usr/bin/env python
"""Merge sort a singly linked linear list."""
import random
from itertools import product

# Linked list is either empty or a value and a link to the next list
empty = None # empty list

class LL(object):
    __slots__ = "value", "next"
    def __init__(self, value, next=empty):
        self.value = value
        self.next = next

def llistsort(head):
    """Translation from C to Python of listsort() [1].

    O(N log N) (best & worst) -time, O(1)-space
    inplace Mergesort algorithm for a singly linked linear list [2]

    >>> head = mklist([2, 3, 1])
    >>> tolist(head)
    [2, 3, 1]
    >>> tolist(llistsort(head))
    [1, 2, 3]

    [1]: http://www.chiark.greenend.org.uk/~sgtatham/algorithms/listsort.c
    [2]: http://www.chiark.greenend.org.uk/~sgtatham/algorithms/listsort.html
    """
    insize = 1 # lists of size 1 are always sorted
    while True: # merge adjacent pairs of `insize`-sized sorted lists
        if __debug__: # check the loop invariant
            pairwise = lambda L: zip(L, L[1:])
            issorted = lambda L: all(x <= y for x, y in pairwise(L))
            # all adjacent `insize`-sized lists are sorted
            lst = tolist(head)
            assert all(issorted(lst[i:i+insize])
                       for i in range(0, len(lst), insize))
        p = head # head of the left list to be merged
        head, tail = empty, empty # head and tail of the output list
        nmerges = 0 # count number of merges we do in this pass
        while p is not empty:
            nmerges += 1 # there exists a merge to be done

            # step `insize' places along from p or until the end of
            #   the list, whichever comes first
            q = p # head of the right list to be merged
            for psize in range(1, insize + 1):
                q = q.next
                if q is empty: # the end of the list (q is empty list)
                    break
            qsize = insize

            # merge a list starting at p, of length psize, with a list
            #   starting at q of length *at most* qsize
            while psize > 0 or (qsize > 0  and q is not empty):
                # decide whether next element of merge comes from p or q
                if psize == 0: # p is empty
                    e, q = q, q.next # e must come from q, pop q
                    qsize -= 1
                elif qsize == 0 or q is empty: # q is empty
                    e, p = p, p.next # e must come from p, pop p
                    psize -= 1
                elif p.value <= q.value: # first element of p is lower or same
                    # choose p in the case of `p.value == q.value` to
                    # maintain sort stability
                    e, p = p, p.next # e must come from p, pop p
                    psize -= 1
                else: # p.value > q.value i.e., first element of q is lower
                    e, q = q, q.next # e must come from q, pop q
                    qsize -= 1

                # add e to the end of the output list
                if tail is not empty:
                    tail.next = e
                else: # 1st iteration
                    head = e # smallest item among two lists
                tail = e
            # now p has stepped `insize' places along, and q has too (or eol)
            p = q # move to the next pair of lists to merge
        #end of while p is not empty:

        if tail is not empty:
            tail.next = empty # terminate the output list

        # if we have done only one merge, we're finished
        if nmerges <= 1: # allow for nmerges==0, the empty list case
            return head
        else:# otherwise repeat, merging lists twice the size
            insize *= 2

def mklist(initializer):
    it = reversed(initializer)
    try:
        x = next(it)
    except StopIteration:
        return empty # empty list
    else:
        head = LL(x)
        for value in it:
            head = LL(value, head)
        return head

def walk(head):
    while head is not empty:
        yield head.value
        head = head.next

def tolist(head):
    return list(walk(head))

def test():
    for n, r, k in product(range(10), repeat=3):
        L = list(range(n)) + [n//2]*r + [n-1]*k
        random.shuffle(L)
        head = mklist(L)
        assert tolist(head) == L
        head = llistsort(head)
        assert tolist(head) == sorted(L)

if __name__ == "__main__":
    import doctest; doctest.testmod()
    test()
