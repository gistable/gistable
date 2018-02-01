#!/usr/bin/python
import uuid
import os
from zipfile import ZipFile, is_zipfile
import sys
import time
from random import randint
import argparse
import re

# To avoid confusing with DAZ3D product codes, some special ranges need to be used, so the following ranges has been reserved:
#
# - 3xxxxxxx    for Hivewire3D                         , where xxxxxxx is the product number without the prefix letter.
# - 4xxxxxxx    for RuntimeDNA                         , where xxxxxxx is the product number without the prefix letter.
# - 5xxxxxxx    for Most Digital Creations products    , where xxxxxxx is the product number without the prefix letter.
# - 6xxxxxxx    for Sharecg products                   , where xxxxxxx is the reference number.
# - 7xxxxxxx    for Renderosity products               , where xxxxxxx is RO number.
# - 8xxxxxxx    for Wilmap's Digital Creations products, where xxxxxxx is SKU number.
# - 9xxxxxxx    is reserved for your own products      , and can be numbered as your convenience.
#
# ie: the SKU 41367 (Renderotica SFD pubic hair for V5) will be converted in an zip archive named IM80041367-00_SFDPubicHairForV5.zip
#
# Another tips is to add the "CVN" letters at the end of the productname, so that it can be easily identified as "converted".

idmap = {
    'HW'   : 3,
    'RDNA' : 4,
    'MDC'  : 5,
    'SCG'  : 6,
    'RO'   : 7,
    'WDC'  : 8,
    'ME'   : 9,
}

dsx = """\
<?xml version="1.0" encoding="UTF-8"?>
<ProductSupplement VERSION="0.1">
 <ProductName VALUE="{pname}"/>
 <ProductStoreIDX VALUE="{pidx}-{psubidx}"/>
 <UserOrderId VALUE="{orderid}"/>
 <UserOrderDate VALUE="{orderdate}"/>
 <InstallerDate VALUE="{installerdate}"/>
 <ProductFileGuid VALUE="{guid}"/>
 <InstallTypes VALUE="Content"/>
 <ProductTags VALUE="DAZStudio4_5"/>
</ProductSupplement>
"""
manifest_header = """\
<DAZInstallManifest VERSION="0.1">
 <GlobalID VALUE="{}"/>"""
manifest_line = """ <File TARGET="Content" ACTION="Install" VALUE="{}"/>"""
manifest_footer = """</DAZInstallManifest>
"""

supplement = """\
<ProductSupplement VERSION="0.1">
 <ProductName VALUE="{}"/>
 <InstallTypes VALUE="Content"/>
 <ProductTags VALUE="DAZStudio4_5"/>
</ProductSupplement>
"""
def zipVerified(thePath):
    rootdirs = set(['data', 'Runtime', 'People', 'Scripts', 'Shaders', 'Presets', 'Shader Presets', 'Materials'])
    with ZipFile(thePath,'r') as zip:
        names = zip.namelist()
        dirs = set([ i[:i.index('/')] for i in names if i.count('/')])

    if not rootdirs.intersection(dirs):
        return False
    return True

def addDirContent(zip, thePath):
    prefix = os.path.dirname(thePath)
    manifest = [manifest_header.format(str(uuid.uuid4()))]

    for dirpath, dirnames, filenames in os.walk(thePath):
        for filename in filenames:
            fullPath = os.path.join(dirpath, filename)
            filePath = os.path.join('Content',fullPath[len(prefix)+1:])
            filePath = filePath.replace('&', '&amp;')
            manifest.append(manifest_line.format(filePath))
            zip.writestr(filePath, open(fullPath,'r').read())
    manifest.append(manifest_footer)
    return manifest

def addZipContent(zip, thePath):
    manifest = [manifest_header.format(str(uuid.uuid4()))]

    with ZipFile(thePath, 'r') as infile:
        for name in infile.namelist():
            info = infile.getinfo(name)
            if info.external_attr & 16:
                continue
            filePath = os.path.join('Content', name)
            filePath = filePath.replace('&', '&amp;')
            manifest.append(manifest_line.format(filePath))
            zip.writestr(filePath, infile.read(name))
    manifest.append(manifest_footer)
    return manifest

def makeDSX(dsxname, productid, productpart, productname):
    dsxinfo = {
        'orderdate'     : time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
        'installerdate' : time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
        'guid'          : str(uuid.uuid4()),
        'pidx'          : productid,
        'psubidx'       : productpart,
        'pname'         : productname,
        'orderid'       : randint(1000000,9999999),
    }
    dsxbytes = dsx.format(**dsxinfo)

    with open(os.path.join(os.getcwd(), dsxname),'w') as dsxfile:
        dsxfile.write(dsxbytes)

def main():
    parser = argparse.ArgumentParser(description='Make DAZ Install manager ZIP and metadata.')
    parser.add_argument('contents', metavar='directory or zip', type=str, help='Product input source (directory or zip file)')
    parser.add_argument('--prefix', dest='prefix', type=int, help='Manufacturer prefix')
    parser.add_argument('--source', dest='source', type=str, choices=(idmap.keys() + map(str.lower, idmap.keys())), help='Manufacturers Product ID')
    parser.add_argument('--id', dest='productid', type=int, help='Manufacturers Product ID')
    parser.add_argument('--part', dest='productpart', type=int, help='Part of product')
    parser.add_argument('--name', dest='productname', type=str, help='Name of product')

    args = parser.parse_args()

    prefix = args.prefix if args.prefix else idmap[args.source.upper()]

    if is_zipfile(args.contents):
        if zipVerified(args.contents):
            pass
        else:
            print "Input ZIP", args.contents, "is not organized correctly. Extract and retry with directory."
            return
    elif os.path.isdir(args.contents):
        pass
    else:
        print "Input must be either a directory or zipfile"
        return

    productid = 10000000*prefix + args.productid
    productname = re.sub('[^\w\d]', '', args.productname)
    zipname = "IM{:8d}-{:02d}_{}.zip".format(productid, args.productpart, productname)
    dsxname = "IM{:8d}-{:02d}_{}.dsx".format(productid, args.productpart, productname)
    print 'Creating {} from {}'.format(zipname, args.contents)
    with ZipFile(os.path.join(os.getcwd(), zipname), 'w') as zip:
        if is_zipfile(args.contents):
            manifest = addZipContent(zip, args.contents)
        else:
            manifest = addDirContent(zip, args.contents)
        manifestbytes = "\n".join(manifest)
        supplementbytes = supplement.format(args.productname)
        zip.writestr('Supplement.dsx', supplementbytes);
        zip.writestr('Manifest.dsx', manifestbytes)

    makeDSX(dsxname, productid, args.productpart, args.productname)

if __name__ == "__main__":
    main()
