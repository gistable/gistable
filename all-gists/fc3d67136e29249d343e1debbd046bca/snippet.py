import os, sys, re

dir =    sys.argv[1] if len(sys.argv) > 1 else "files"
find =   sys.argv[2] if len(sys.argv) > 2 else "<\?\n"
set_to = sys.argv[3] if len(sys.argv) > 3 else "<?PHP\n"
exts =   sys.argv[4] if len(sys.argv) > 4 else "\.php|\.txt"

pattern = re.compile(find, re.I | re.M | re.S)

if not os.path.isdir(dir):
  print dir + " does not exist!"
  sys.exit(0)

for root, subFolders, files in os.walk(dir):
  for file in files:
    if re.search(exts, file):
      filename = os.path.join(root, file)
      f = open(filename, "r+")
      s = f.read()
      f.seek(0)
      f.write(pattern.sub(set_to, s))
      f.truncate()
      f.close()
      print filename + " updated."
