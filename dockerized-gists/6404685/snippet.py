# create a new set and add values
myset = set()
myset.add(1)
myset.add(2)
myset.add(4)

# by default, a set returns a set Object
# myset = set([1, 2, 4])
# use join() to parse the List into a str

','.join(str(s) for s in myset)
'1,2,4'