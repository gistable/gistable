#!/usr/bin/env python
import httplib, os.path, argparse, pefile, struct

"""
pdb_downloader.py
v0.1

Steeve Barbeau
@steevebarbeau
steeve-barbeau.blogspot.com

$ ./pdb.py --dll lsasrv.dll
Downloading file ...
Done"
Now   run `cabextract lsasrv.pd_` to extract PDB file from the CAB file

"""

url = "/download/symbols/%s.pdb/%s/%s.pd_"

def download_pdb(dll_name, guid):
  conn = httplib.HTTPConnection("msdl.microsoft.com")
  headers = {"User-Agent": "Microsoft-Symbol-Server/6.12.0002.633"}
  conn.request("GET", url % (dll_name, guid, dll_name), "", headers)
  
  response = conn.getresponse()
  
  if response.status == 200:
    print "Downloading file ..."
    pdb_buffer = response.read()
  
    pdb_filename = os.path.basename(url % (dll_name, guid, dll_name))
    pdb_file = open(pdb_filename, 'w')
    pdb_file.write(pdb_buffer)
    pdb_file.close()
     
    print """\tDone"
Now run `cabextract %s` to extract PDB file from the CAB file""" % pdb_filename
  else:
    print "FAIL"


def get_guid(dll_path):
  # ugly code, isn't it ?
  try:
    dll = pefile.PE(dll_path)
    rva = dll.DIRECTORY_ENTRY_DEBUG[0].struct.AddressOfRawData
    tmp = ''
    tmp += '%0.*X' % (8, dll.get_dword_at_rva(rva+4))
    tmp += '%0.*X' % (4, dll.get_word_at_rva(rva+4+4))
    tmp += '%0.*X' % (4, dll.get_word_at_rva(rva+4+4+2))
    x = dll.get_word_at_rva(rva+4+4+2+2)
    tmp += '%0.*X' % (4, struct.unpack('<H',struct.pack('>H',x))[0])
    x = dll.get_word_at_rva(rva+4+4+2+2+2)
    tmp += '%0.*X' % (4, struct.unpack('<H',struct.pack('>H',x))[0])
    x = dll.get_word_at_rva(rva+4+4+2+2+2+2)
    tmp += '%0.*X' % (4, struct.unpack('<H',struct.pack('>H',x))[0])
    x = dll.get_word_at_rva(rva+4+4+2+2+2+2+2)
    tmp += '%0.*X' % (4, struct.unpack('<H',struct.pack('>H',x))[0])
    tmp += '%0.*X' % (1, dll.get_word_at_rva(rva+4+4+2+2+2+2+2+2))
  except AttributeError, e:
    print 'Error appends during %s parsing' % dll_path
    print e
    return None
  return tmp.upper()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--dll', dest='dll', help='Path of the DLL')
  args = parser.parse_args()
  if args.dll:
    if os.path.isfile(args.dll):
      guid = get_guid(args.dll)
      if guid:
        download_pdb( os.path.splitext(os.path.basename(args.dll))[0], guid)
      else:
        print "/!\ Fail to calculate GUID"
    else:
      print "/!\ File %s doesn't exist" % args.dll
  else:
    parser.print_help()