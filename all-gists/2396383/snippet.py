import random


def insert_sort(l):
    for i, item in enumerate(l):
        while i > 0 and l[i - 1] > item:
            l[i] = l[i - 1]
            i -= 1
        l[i] = item


things = range(10)
random.shuffle(things)
print things
insert_sort(things)
print things
