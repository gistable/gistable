import os, glob, shutil, sys

path = os.environ['LOCALAPPDATA'] + "/Google/Chrome/User Data/Default/Cache/"
listing = os.listdir(path)
for infile in listing:
  if "f_" in infile:
    abs_path = path + infile
    statinfo = os.stat(abs_path)

    if statinfo.st_size > 1000000: #checking to see if the file > 1MB
      print 'Checking ' + infile + ' | Name: ' + repr(statinfo.st_size) + ' | Size: ' + repr(statinfo.st_size) 
      print statinfo
      if not "mp3" in infile:
        newfile = abs_path + '.mp3'
        print 'Renaming: ' + newfile
        os.rename(abs_path, newfile)
        abs_path = newfile
        infile += ".mp3"
        
      #TODO: Set this value for destination directory
      dest = ""
      if "mp3" in infile:
        try:
          shutil.move(abs_path, dest)
        except:
          print "Unexpected error:", sys.exc_info()[0]