elements = sorted([1, 2, 8, 4, 5, 2, 6, 9, 12, 5])
count = len(elements)
ninty = int(count * .1)
for i in range(ninty):
  print elements.pop()