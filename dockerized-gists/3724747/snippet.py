import sys

class HashTable:
  def __init__(self):
    self.fill = 8 # Active + # Dummy
    self.list = [0] * self.fill
    self.used = 0 # Active
  def __getitem__(self, slot):
    return self.list[slot]
  def insert(self, slot, key):
    self.used += 1
    self.list[slot] = key

    if self.used > 2 * self.fill /3:
      #print "self.used: %i" % self.used
      #print "self.fill: %i" % self.fill
      print "active slots larger than 2/3 max... resizing Table"
    return

def printtable(table):
  s = 0
  print "--------"
  for e in table:
    print "| %i | %s |" % (s, str(e))
    s += 1
  print "--------"
  return


def lookdict(table, key):
  mask = table.fill - 1
  PERTURB_SHIFT = 5

  print "looking up key: %s" % str(key)
  h = hash(key)
  perturb = h
  print "the hash is %i" % h
  i = h & mask
  print "using table slot: %i" % i
  if table[i] == 0:
    table.insert(i, key)
  else:
    c = 1
    #i = 3
    while c <= 15:
      print "#" * 8, "Collision!", "#" * 8
      i = (i << 2) + i + perturb + 1
      perturb >>= PERTURB_SHIFT
      slot = i & mask
      print "probing attempt %i: trying table slot: %i" % (c, slot)
      #print "perturb: %i" % perturb
      if table[slot] == 0:
        table.insert(slot, key)
        break
      else:
        c += 1


  printtable(table)
  return table

if __name__ == '__main__' or __name__ == sys.argv[0]:
  table = HashTable()
  #table = lookdict(table, 'a')
  table = lookdict(table, 'z')
  table = lookdict(table, 'z')
  table = lookdict(table, 'z')
  table = lookdict(table, 'z')
  table = lookdict(table, 'z')
  table = lookdict(table, 'z')
