from itertools import chain

intersection = []

sets = [[0,4,5,2,1],[1,3,6,2,4],[4,1,2,5,7,0]]

merged = list(chain.from_iterable(sets))

merged.sort()

i = 0
while i < (len(merged)-(len(sets)-1)):
    sub = merged[i:(i+len(sets))]
    if sub[0] == sub[len(sub)-1]:
        intersection.append(sub[0])
        i += (len(sub)-1)
    i += 1

print intersection