__author__ = 'schwa'

import glob
import zipfile
import fnmatch
import re
import os

path = '~/Music/iTunes/iTunes Media/Mobile Applications/*.ipa'
path = os.path.expanduser(path)

for f in glob.glob(path):
    z = zipfile.ZipFile(f)
    for framework in  [name for name in z.namelist() if fnmatch.fnmatch(name, 'Payload/*.app/Frameworks/*')]:
        if re.match('.*swift.*', framework):
            print f
            break
