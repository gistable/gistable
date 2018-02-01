import os
import csv
from subprocess import Popen, PIPE
from Foundation import NSMutableDictionary

build_number = os.popen4("git rev-parse --short HEAD")[1].read()
info_plist = os.environ['BUILT_PRODUCTS_DIR'] + "/" + os.environ['WRAPPER_NAME'] + "/Info.plist"

# Open the plist and write the short commit hash as the bundle version
plist = NSMutableDictionary.dictionaryWithContentsOfFile_(info_plist)
core_version = csv.reader([plist['CFBundleVersion'].rstrip()], delimiter=" ").next()[0]
full_version = ''.join([core_version, ' build ', build_number])
plist['CFBundleVersion'] = full_version.rstrip()
plist.writeToFile_atomically_(info_plist, 1)
