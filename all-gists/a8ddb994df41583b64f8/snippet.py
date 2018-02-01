#!/usr/bin/env python

from Foundation import NSData, NSPropertyListSerialization
import fnmatch
import sys
from zipfile import ZipFile

# TODO: Add error checking.

def parse_plist(info_plist_string):
  # Use PyObjC, pre-installed in Apple's Python dist.
  data = NSData.dataWithBytes_length_(info_plist_string, len(info_plist_string))
  return NSPropertyListSerialization.propertyListWithData_options_format_error_(data, 0, None, None)

def parse_ipa_info(ipa_path):
  ipa_zip = ZipFile(ipa_path)
  files = ipa_zip.namelist()
  info_plist = fnmatch.filter(files, "Payload/*.app/Info.plist")[0]
  info_plist_bin = ipa_zip.read(info_plist)
  info = parse_plist(info_plist_bin)[0]
  ipa_zip.close()
  
  return info


if __name__ == "__main__":
  print parse_ipa_info(sys.argv[1])

