# Somewhat manual, pretty hacky 'toolkit' for breaking XECryption

with open ("enc.txt", "r") as encfile:
    encdata=encfile.read().replace('\n', '')

encsplit = encdata.split(".")
#print encsplit

encsplitlen = len(encsplit)
print "Total numbers: {}".format(encsplitlen)
print "Calculated triplets: {}".format(encsplitlen / 3)


pos = 1
triplets = []
while pos < encsplitlen:
  triplet = [encsplit[pos], encsplit[pos+1], encsplit[pos+2]]
  triplets.append(triplet)
  pos += 3

print "\nActual triplet count: {}\n".format(len(triplets))

def makeKey(triplet):
  return int(triplet[0]) + int(triplet[1]) + int(triplet[2])

freq = {}
for triplet in triplets:
  key = makeKey(triplet)

  if key in freq:
    freq[key].append(triplet)
  else:
    freq[key] = [triplet]

#print freq
print "\nFreq length (unique chars): {}\n".format(len(freq))

biggestFreq = 0
for key in freq.keys():
  freqLen = len(freq[key])
  print "{} : {}".format(key, freqLen)

  if freqLen > biggestFreq:
    biggestFreq = freqLen
    space = key

def offsetFromSpace(char):
  space = ord(" ")
  charVal = ord(char)
  return charVal-space

decoded = list(triplets)
#space = 794
encKey = space - 32

for index, item in enumerate(decoded):
  itemKey = makeKey(item)
  itemAsc = itemKey-encKey
  decoded[index] = chr(itemAsc)

print decoded
print "".join(decoded)