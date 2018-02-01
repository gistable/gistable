#!/usr/bin/env python
"""
nzbrename - A utility for renaming mangled NZBs.

Almost all of the NNTP and yenc stuff is taken from SabNZBd.

Requires:
  * par2ools
  * pynzb
"""

import binascii
import hashlib
import locale
import logging
import nntplib
import pynzb        # TODO: Remove this dependency
import re
import sys

from par2ools import par2
from StringIO import StringIO
from xml.dom import minidom

# NNTP server settings - SSL not yet supported
HOST = ""
PORT = 119
USER = ""
PASS = ""

#############################
##  Don't edit below here  ##
#############################

CHUNK = 16384   # 16KB

PAR2_MAIN_RE = re.compile(r'\.par2')
PAR2_VOL_RE  = re.compile(r'\.vol[\d]+\+[\d]+\.par2')
RE_NORMAL_NAME = re.compile(r'\.\w{1,5}$') # Test reasonably sized extension at the end
SUBJECT_FN_MATCHER = re.compile(r'"([^"]*)"')

NZB_TEMPLATE = """
<?xml version="1.0" ?>
<!DOCTYPE nzb PUBLIC '-//newzBin//DTD NZB 1.1//EN' 'http://www.newzbin.com/DTD/nzb/nzb-1.1.dtd'>
<nzb xmlns="http://www.newzbin.com/DTD/2003/nzb">
</nzb>
"""

gUTF = False
def auto_fsys():
    global gUTF
    try:
        if sabnzbd.DARWIN:
            gUTF = True
        else:
            gUTF = locale.getdefaultlocale()[1].lower().find('utf') >= 0
    except:
        # Incorrect locale implementation, assume the worst
        gUTF = False

def platform_encode(p):
    """ Return the correct encoding for the platform:
        Latin-1 for Windows/Posix-non-UTF and UTF-8 for OSX/Posix-UTF
    """
    if isinstance(p, unicode):
        if gUTF:
            return p.encode('utf-8')
        else:
            return p.encode('latin-1', 'replace')
    elif isinstance(p, basestring):
        if gUTF:
            try:
                p.decode('utf-8')
                return p
            except:
                return p.decode('latin-1').encode('utf-8')
        else:
            try:
                return p.decode('utf-8').encode('latin-1', 'replace')
            except:
                return p
    else:
        return p

def name_extractor(subject):
    """ Try to extract a file name from a subject line, return `subject` if in doubt
    """
    result = subject
    for name in re.findall(SUBJECT_FN_MATCHER, subject):
        name = name.strip(' "')
        if name and RE_NORMAL_NAME.search(name):
            result = name
    return platform_encode(result)

def name_fixer(p):
    """ Return UTF-8 encoded string, if appropriate for the platform """

    if gUTF and p:
        return p.decode('Latin-1', 'replace').encode('utf-8', 'replace').replace('?', '_')
    else:
        return p

YSPLIT_RE = re.compile(r'([a-zA-Z0-9]+)=')
def ySplit(line, splits = None):
    fields = {}

    if splits:
        parts = YSPLIT_RE.split(line, splits)[1:]
    else:
        parts = YSPLIT_RE.split(line)[1:]

    if len(parts) % 2:
        return fields

    for i in range(0, len(parts), 2):
        key, value = parts[i], parts[i+1]
        fields[key] = value.strip()

    return fields

def yCheck(data):
    ybegin = None
    ypart  = None
    yend   = None

    ## Check head
    for i in xrange(min(40, len(data))):
        try:
            if data[i].startswith('=ybegin '):
                splits = 3
                if data[i].find(' part=') > 0:
                    splits += 1
                if data[i].find(' total=') > 0:
                    splits += 1

                ybegin = ySplit(data[i], splits)

                if data[i+1].startswith('=ypart '):
                    ypart = ySplit(data[i+1])
                    data = data[i+2:]
                    break
                else:
                    data = data[i+1:]
                    break
        except IndexError:
            break

    ## Check tail
    for i in xrange(-1, -11, -1):
        try:
            if data[i].startswith('=yend '):
                yend = ySplit(data[i])
                data = data[:i]
                break
        except IndexError:
            break

    return ((ybegin, ypart, yend), data)

def strip(data):
    while data and not data[0]:
        data.pop(0)

    while data and not data[-1]:
        data.pop()

    for i in xrange(len(data)):
        if data[i][:2] == '..':
            data[i] = data[i][1:]
    return data

YDEC_TRANS   = ''.join([chr((i + 256 - 42) % 256) for i in xrange(256)])
def yenc_decode(data):
    data = ''.join(data)
    for i in (0, 9, 10, 13, 27, 32, 46, 61):
        j = '=%c' % (i + 64)
        data = data.replace(j, chr(i))
    decoded_data = data.translate(YDEC_TRANS)
    crc = binascii.crc32(decoded_data)
    partcrc = '%08X' % (crc & 2**32L - 1)

    return decoded_data, crc, partcrc

def decode(data):
    filename = None
    data     = strip(data)

    if data:
        yenc, data = yCheck(data)
        ybegin, ypart, yend = yenc
        decoded_data = None
        
        if not (ybegin and yend):
            logging.error("File encoding not supported")
            return

        if 'name' in ybegin:
            filename = name_fixer(ybegin['name'])
            logging.debug("Filename: '%s'" % filename)
        else:
            logging.error("Couldn't determine filename")

        decoded_data, crc, partcrc = yenc_decode(data)
        if ypart:
            crcname = 'pcrc32'
        else:
            crcname = 'crc32'

        if crcname in yend:
            _partcrc = '0' * (8 - len(yend[crcname])) + yend[crcname].upper()
        else:
            _partcrc = None
            logging.error("Corrupt header detected " + \
                          "=> yend: %s", yend)
            return

        if not (_partcrc == partcrc):
            logging.error("CRC mismatch")
            return

        return filename, decoded_data

def get_par2(nzb, all=False):
    parfiles = []
    parmap   = {}

    for f in nzb:
        if PAR2_MAIN_RE.search(f.subject):
            if not PAR2_VOL_RE.search(f.subject):
                name = name_extractor(f.subject)
                logging.info("Found par file: '%s'" % name)
                parmap[f] = 0
                f.filename = name
                parfiles.append(f)

    logging.info("Found %d par2 files" % len(parfiles))

    if all:
        return parfiles

    for parfile in parfiles:
        nzb.remove(parfile)
        basename = parfile.filename.split('.par2')[0]

        for f in nzb:
            filename = name_extractor(f.subject)
            if filename.find(basename) > -1:
                parmap[parfile] += 1

    max_count   = 0
    parfile     = None
    for pf, count in parmap.items():
        if count > max_count:
            max_count = count
            parfile = pf

    return parfile

def run(nzbpath):
    hashmap = {}
    filemap = {}

    logging.info("Connecting to NNTP server")
    nntp = nntplib.NNTP(HOST, PORT, USER, PASS)

    logging.info("Parsing NZB")
    nzbdata = open(nzbpath).read()
    nzb = pynzb.nzb_parser.parse(nzbdata)

    logging.info('NZB contains %d files' % len(nzb))

    parfiles = get_par2(nzb, True)

    if parfiles is None:
        logging.error("Couldn't find and par2 files")
        return

    for parfile in parfiles:
        logging.info("Processing par2: '%s'" % parfile.filename)
        logging.info("  Downloading par2 file")

        if len(parfile.segments) !=  1:
            logging.error("  Multi-segment par2 files are not currently supported")
            return

        article = nntp.body('<%s>' % parfile.segments[0].message_id)
        resp = decode(article[3])
        if resp:
            filename, pardata = resp
        else:
            logging.error("  Error getting article: %s" % parfile.name)
            return

        if not pardata:
            logging.error("  Error decoding article")
            return

        par2file = par2.Par2File(StringIO(pardata))
        logging.info("  Par file contains %d packets" % len(par2file.packets))
        
        logging.debug("  Building hashmap")
        for pkt in par2file.packets:
            if isinstance(pkt, par2.FileDescriptionPacket):
                hashmap[pkt.file_hash16k] = pkt.name
        
        padding = max([len(name_extractor(f.subject)) for f in nzb])+2
        format = "  %%-%ds -> %%s" % padding
        matches = []
        for i, f in enumerate(nzb):
            sys.stdout.write("  %d/%d\r" % (i+1,len(nzb)))
            sys.stdout.flush()

            article = nntp.body('<%s>' % f.segments[0].message_id)
            resp = decode(article[3])
            if resp:
                filename, data = resp
            else:
                logging.error("  Error getting article: %s" % f.name)
                continue

            md5  = hashlib.md5(data[:CHUNK]).digest()
            if hashmap.has_key(md5):
                filemap[filename] = hashmap[md5]
                print format % (filename, filemap[filename])
                matches.append(f)
            else:
                print format % (filename, filename)
        
        for f in matches:
            nzb.remove(f)

    logging.info("Disconnecting from NNTP server")
    nntp.quit()
    
    ###
    #   Create a new nzb
    ###
    nzbpath = nzbpath.replace(".nzb", "-renamed.nzb")
    print "Creating new nzb '%s'" % nzbpath

    nzb = minidom.parseString(nzbdata)
    for f in nzb.getElementsByTagName("file"):
        subject  = f.attributes.get("subject").value
        filename = name_extractor(subject)
        new_filename = filemap.get(filename)
        if filename and new_filename:
            #print "Renaming '%s' -> '%s'" % (filename, new_filename)
            f.attributes["subject"] = subject.replace(filename, new_filename)
        #else:
            #print "No match for '%s" % filename

    nzb_out = open(nzbpath, "w")
    for line in nzb.toprettyxml(indent=" ").split("\n"):
        if not line.strip().strip("\n"):
            continue
        nzb_out.write(line+"\n")
    nzb_out.close()

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")
    if len(sys.argv) < 2:
        print "Usage: %s <nzb>" % sys.argv[0]
        sys.exit(-1)

    auto_fsys()

    run(sys.argv[1])
