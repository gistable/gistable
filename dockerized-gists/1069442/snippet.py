from hashlib import sha1


def main():
  print hashfile("~/Desktop/lift-columns.png")

def hashfile(path):
  f = open(path)
  file_hash = githash(f.read())
  f.close()
  return file_hash

def githash(data):
    s = sha1()
    s.update("blob %u\0" % len(data))
    s.update(data)
    return s.hexdigest()


if __name__ == '__main__':
  main()