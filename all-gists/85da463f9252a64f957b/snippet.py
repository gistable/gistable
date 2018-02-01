# extract ILSVRC2012 without killing your SSD

import tarfile
import os
import sys

def mkdir(x):
  try:
    os.makedirs(x)
  except OSError, e:
    pass

def extract(dat):
  mkdir(dat)

  tar = tarfile.open("ILSVRC2012_img_"+dat+".tar")

  for tarinfo in tar:
    basedir = dat+"/"+tarinfo.name.split(".")[0]+"/"
    print "extracting %11d to %s" % (tarinfo.size, basedir)
    mkdir(basedir)
    ifile = tar.extractfile(tarinfo)

    itar = tarfile.open(mode="r", fileobj=ifile)
    itar.extractall(path=basedir)
    itar.close()

    ifile.close()

  tar.close()

extract(sys.argv[1])