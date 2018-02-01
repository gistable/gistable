import sys

salesTotal = 0
oldKey = None

for line in sys.stdin:
    data = line.strip().split("\t")
    if len(data) != 2:
        # Something has gone wrong. Skip this line.
        continue

    thisKey, thisSale = data
    if oldKey and oldKey != thisKey:
      print oldKey, "\t", salesTotal
      oldKey = thisKey
      salesTotal = 0

     oldKey = thisKey
     salesTotal += float(thisSale)

 if oldKey != None:
   print oldKey, "\t", salesTotal