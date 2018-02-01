class machine(object):
  def __init__(self):
    self.inscount = 0
    self.storage = []

  # CMP: instype 0, k1=pos, k2=byte, k3=switch1(-1), k4=switch2(0), k5=switch3(1)
  # KV: instype 1, key, value
  def add_inst(self, instype, k1=-1, k2=-1, k3=-1, k4=-1, k5=-1):
    if instype == 0:
      if k1 < 0: raise
      if k2 < 0 or k2 > 255: raise
    self.storage.append((instype, k1, k2, k3, k4, k5))
    self.inscount += 1

  def run(self, query):
    cp = 0
    while True:
      if cp < 0:
        break
      ins = self.storage[cp]
      instype = ins[0]
      if instype == 0: # CMP
        # Note: currently we do not limit back jump
        if ins[3] >= self.inscount: raise
        if ins[4] >= self.inscount: raise
        if ins[5] >= self.inscount: raise
        if len(query) <= ins[1]:
          cp = ins[3]
          continue
        o = ord(query[ins[1]])
        if o < ins[2]:
          cp = ins[3]
        elif o == ins[2]:
          cp = ins[4]
        else:
          cp = ins[5]
      elif instype == 1: # KV
        if query == ins[1]:
          return ins[2]
        return None
      else:
        raise Exception('unknown op')
    return None

if __name__ == '__main__':
  a = machine()
  a.add_inst(0, 0, ord('a'), -1, 1, 2)
  a.add_inst(1, 'a', 'b')
  a.add_inst(1, 'b', 'c')
  print(a.run('a'))
  print(a.run('b'))