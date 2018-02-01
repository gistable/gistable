def array_chunk(arr, size):
  chunks=[arr[x:x+size] for x in xrange(0, len(arr), size)]