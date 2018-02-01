def human_readable_to_bytes(size):
   """Given a human-readable byte string (e.g. 2G, 10GB, 30MB, 20KB),
      return the number of bytes.  Will return 0 if the argument has
      unexpected form.
   """
   if (size[-1] == 'B'):
      size = size[:-1]
   if (size.isdigit()):
      bytes = int(size)
   else:
      bytes = size[:-1]
      unit = size[-1]
      if (bytes.isdigit()):
         bytes = int(bytes)
         if (unit == 'G'):
            bytes *= 1073741824
         elif (unit == 'M'):
            bytes *= 1048576
         elif (unit == 'K'):
            bytes *= 1024
         else:
            bytes = 0
      else:
         bytes = 0
return bytes,size+'B'
