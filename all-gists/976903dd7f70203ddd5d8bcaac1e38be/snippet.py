import sys
import os.path

def main(files):
    nfiles = len(files)
    if nfiles < 2:
      sys.exit("Usage: %s file1 file2 ... " % sys.argv[0])

    # Check files
    for filename in files:
      if( os.path.isfile(filename) == False ):
        sys.exit("File %s not found" % filename)

    # read files
    n = 0
    d = []
    for filename in files:
      f = open(filename, 'r') 
      d.append(f.read())
      n += 1

    # compare and print
    for i in range(len(d[0])):
      a = d[0][i]
      for x in range(1,nfiles):
        if a != d[x][i]:
          sys.stdout.write("_")
          break
      else:
        sys.stdout.write(a) 

if __name__ == '__main__':
    main(sys.argv[1:])
    