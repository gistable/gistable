# 
# http://stackoverflow.com/questions/519633/lazy-method-for-reading-big-file-in-python
#

def readline_in_chunks(file_object, chunk_size=1024):
  buf = ''
  while True:
    data = file_object.read(chunk_size)
    if not data:
      break
    buf = buf + data
    while True:
      pos = buf.find('\n')
      if pos < 0:
        break
      yield buf[:pos]
      buf = buf[pos+1:]

def main():
  f = open('test.txt', 'r')
  for line in readline_in_chunks(f):
    print line

if __name__ == '__main__':
  main()