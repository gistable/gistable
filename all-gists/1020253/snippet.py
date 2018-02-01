from string import digits

x = ["1a", "2b", "2b", "3c", "5e"]

#the clearest, most basic way I can think of
numbers = {}
for i in x:
    first = i[0]
    if first in digits:
        if first in numbers:
            numbers[first] += 1
        else:
            numbers[i[0]] = 1

for i in digits:
    if i not in numbers:
        print "0 %s's" % (i)
    else:
        print "%s %s's" % (numbers[i], i)

print "================="

#here's one way to simplify it:
# http://docs.python.org/library/collections.html#collections.Counter

from collections import Counter

numbers = Counter()
for i in x:
    if i[0] in digits:
        numbers[i[0]] += 1

#a counter's value defaults to 0, so we don't need to check if we've set it yet or not
for i in digits:
    print "%s %s's" % (numbers[i], i)

print "================="

#here's another
# (don't do this, it's here for neato value :)
print {i:sum(j[0]==i for j in x) for i in map(str, range(10))}

print "================="

#the equivalent of @agnellvj's answer:
numbers = {}
for i in x:
    numbers[i[0]] = numbers.setdefault(i[0], 0) + 1

for i in digits:
    if i not in numbers:
        print "0 %s's" % (i)
    else:
        print "%s %s's" % (numbers[i], i)
