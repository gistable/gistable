#!/usr/bin/python
# modify_basesystem_dmg.py
#
# Adds additional frameworks to BaseSystem.dmg - Python is default
# Modify cpioextract() and xar_source to change what is extracted,
# and from what OS X installer PKG.
#
# To invoke:
#
# ./modify_basesystem_dmg.py /path/to/InstallESD.dmg
#  or
# ./modify_basesystem_dmg.py /path/to/InstallESD.dmg debug
# 

import sys
import os
import subprocess
import tempfile
import plistlib
import shutil
import struct

TMPDIR = None
TMPDIR = tempfile.mkdtemp(dir=TMPDIR)
debug = False

if 'debug' in sys.argv:
    debug = True

print('Staging sources in %s' % TMPDIR)

# Placeholder, remove later
source = sys.argv[1]

installesdshadow = os.path.join(TMPDIR, 'InstallESD.shadow')
basesystemshadow = os.path.join(TMPDIR, 'BaseSystem.shadow')

hdiutil = '/usr/bin/hdiutil'

def dmgattach(attach_source, shadow_file):
    return [ hdiutil, 'attach', '-shadow', shadow_file, '-mountRandom', TMPDIR, '-nobrowse', '-plist', '-owners', 'on', attach_source ]
def dmgdetach(detach_mountpoint):
    return [ hdiutil, 'detach', detach_mountpoint ]
def dmgconvert(convert_source, convert_target, shadow_file):
    return [ hdiutil, 'convert', '-format', 'UDRO', '-o', convert_target, '-shadow', shadow_file, convert_source ]
def dmgresize(resize_source, shadow_file):
    return [ hdiutil, 'resize', '-size', '10G', '-shadow', shadow_file, resize_source ]
def xarextract(xar_source):
    return [ '/usr/bin/xar', '-x', '-f', xar_source, 'Payload', '-C', TMPDIR ]
def cpioextract(cpio_source):
    return [ '/usr/bin/cpio -idmuv -I %s \"*Py*\" \"*py*\"' % cpio_source ]
def getfiletype(filepath):
    return ['/usr/bin/file', filepath]

def runcmd(cmd, cwd=None):

    if debug:
        print('Running command:\n%s' % cmd)

    if type(cwd) is not str:
        proc = subprocess.Popen(cmd, bufsize=-1,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (result, err) = proc.communicate()
    else:
        proc = subprocess.Popen(cmd, bufsize=-1,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd,
                        shell=True)
        (result, err) = proc.communicate()

    if proc.returncode:
        print >> sys.stderr, 'Error "%s" while running command %s' % (err, cmd)

    return result

def parse_pbzx(pbzx_path, xar_out_path):
    f = open(pbzx_path, 'rb')
    pbzx = f.read()
    f.close()
    magic, pbzx = pbzx[:4],pbzx[4:]
    if magic != 'pbzx':
        raise "Error: Not a pbzx file"
    # Read 8 bytes for initial flags
    flags, pbzx = pbzx[:8],pbzx[8:]
    # Interpret the flags as a 64-bit big-endian unsigned int
    flags = struct.unpack('>Q', flags)[0]
    xar_f = open(xar_out_path, 'wb')
    while (flags & (1 << 24)):
        # Read in more flags
        flags, pbzx = pbzx[:8],pbzx[8:]
        flags = struct.unpack('>Q', flags)[0]
        # Read in length
        f_length, pbzx = pbzx[:8],pbzx[8:]
        f_length = struct.unpack('>Q', f_length)[0]
        xzmagic, pbzx = pbzx[:6],pbzx[6:]
        if xzmagic != '\xfd7zXZ\x00':
            xar_f.close()
            raise "Error: Header is not xar file header"
        f_length -= 6
        f_content, pbzx = pbzx[:f_length],pbzx[f_length:]
        if f_content[-2:] != 'YZ':
            xar_f.close()
            raise "Error: Footer is not xar file footer"
        xar_f.write(xzmagic)
        xar_f.write(f_content)
    try:
        xar_f.close()
    except:
        pass


# Resize InstallESD.dmg using shadow file
print('Preparing InstallESD...')
plist = runcmd(dmgresize(source, installesdshadow))

# Mount InstallESD.dmg with resize-shadow file
print('Mounting InstallESD...')
plist = runcmd(dmgattach(source, installesdshadow))
installesdplist = plistlib.readPlistFromString(plist)

for entity in installesdplist['system-entities']:
    if 'mount-point' in entity:
        installesdmountpoint = entity['mount-point']

print('InstallESD mountpoint is %s' % installesdmountpoint)

# Resize BaseSystem.dmg using shadow file
print('Preparing BaseSystem...')
basesystemdmg = os.path.join(installesdmountpoint, 'BaseSystem.dmg')
plist = runcmd(dmgresize(basesystemdmg, basesystemshadow))

# Mount BaseSystem.dmg with shadow file
print('Mounting BaseSystem...')
plist = runcmd(dmgattach(basesystemdmg, basesystemshadow))
basesystemplist = plistlib.readPlistFromString(plist)
for entity in basesystemplist['system-entities']:
    if 'mount-point' in entity:
        basesystemmountpoint = entity['mount-point']

print('BaseSystem mountpoint is %s' % basesystemmountpoint)

# Extract Payload from desired OS X installer package
print('Extracting Payload...')
xar_source = os.path.join(installesdmountpoint, 'Packages', 'BSD.pkg')
result = runcmd(xarextract(xar_source))

print('Determining Payload wrapper...')
payloadsource = os.path.join(TMPDIR, 'Payload')
payloadtype = runcmd(getfiletype(payloadsource)).split(': ')[1]
cpio_source = os.path.join(TMPDIR, 'Payload.cpio.xz')

# Check filetype of the Payload, 10.10 adds a pbzx wrapper
if payloadtype.startswith('data'):
    # Remove pbzx wrapper with parse_pbzx(), save to file
    print('Payload is PBZX-wrapped, processing...')
    parse_pbzx(os.path.join(TMPDIR, 'Payload'), cpio_source)
else:
    # No pbzx wrapper, rename and move to cpio extraction
    print('Payload is not PBZX-wrapped...')
    os.rename(payloadsource, cpio_source)

# Extract all or some (using shell globbing pattern) files from CPIO archive
print('Extracting from Payload into BaseSystem...')
runcmd(cpioextract(cpio_source), cwd=basesystemmountpoint)

# Unmount BaseSystem.dmg
print('Unmounting BaseSystem...')
plist = runcmd(dmgdetach(basesystemmountpoint))

# Convert/save modified BaseSystem.dmg + shadow file to new BaseSystem.dmg
print('Converting BaseSystem...')
basesystemnew = os.path.join(TMPDIR, 'BaseSystemNew.dmg')
plist = runcmd(dmgconvert(basesystemdmg, basesystemnew, basesystemshadow))

# Replace original BaseSystem.dmg with BaseSystemNew.dmg
# Because of weird results when straight mv'ing the new dmg on top of the old
# one we're explicitly removing the original DMG and copying the new one.

print('Replacing original BaseSystem...')
os.remove(basesystemdmg)
shutil.copyfile(basesystemnew, basesystemdmg)

# Unmount InstallESD.dmg
print('Unmounting InstallESD...')
plist = runcmd(dmgdetach(installesdmountpoint))

# Convert/save modified InstallESD.dmg + shadow file to new InstallESD.dmg
print('Converting InstallESD...')
installesdnew = os.path.join(TMPDIR, 'InstallESDNew.dmg')
plist = runcmd(dmgconvert(source, installesdnew, installesdshadow))

# Do clean up
print('Cleaning up...')
os.remove(basesystemnew)
os.remove(installesdshadow)
os.remove(basesystemshadow)
os.remove(cpio_source)
os.remove(os.path.join(TMPDIR, 'Payload'))

shutil.move(installesdnew, os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'InstallESD.dmg'))
shutil.rmtree(TMPDIR)

print('\n*** All done! ***\n\n')
