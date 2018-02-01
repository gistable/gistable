import msgpack
import urllib2


def main():
  m = msgpack.packb(['hello', 12])
  u = urllib2.urlopen('http://localhost:8080/0', m)
  s = u.read()
  u.close()
  print (len(m), len(s))
  v = msgpack.unpackb(s)
  print v

if __name__ == '__main__':
  main()
# vim: ts=2 sts ai
