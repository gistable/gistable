#!/usr/bin/python2
USAGESTR = """Usage: fetchsub.py [-l langcode] videofile1 [videofile2 ...]
    langcode:   chn         [default]
                eng
    sub file will saved in the same directory of each videofile
    XXXXXXX.mkv 's sub files will named as:
    XXXXXXX.chn.0.srt, XXXXXXX.chn.1.srt, XXXXXXX.chn.2.srt
"""

"""Author: sevenever
Original source: http://sevenever.googlecode.com/svn-history/r193/trunk/misc/fetchsub.py

url	see GetUrlByType()
www.shooter.cn/api/subapi.php


post data:
pathinfo	utf8 encoded file path
filehash	utf8 encoded file hash
vhash(optional)	utf8 encode vhash----> see genVHash()
lang(optional)	"eng"
shortname	video short name----> see GetShortFileNameForSearch2_STL()
"""
"""
import socket, ssl
bindsocket = socket.socket()
bindsocket.bind(('', 443))
bindsocket.listen(5)
newsocket, fromaddr = bindsocket.accept()
c = ssl.wrap_socket(newsocket, server_side=True, certfile="server.pem", keyfile="server.pem", ssl_version=ssl.PROTOCOL_SSLv3)
                    
                    
POST /api/subapi.php HTTP/1.0\r\n
User-Agent: SPlayer Build 1476\r\n
Host: www.shooter.cn\r\n
Accept: */*\r\n
Content-Length: 655\r\n
Content-Type: multipart/form-data; boundary=----------------------------ab847ea8ba7a\r\n
\r\n
------------------------------ab847ea8ba7a\r\n
Content-Disposition: form-data; name="pathinfo"\r\n
\r\nD:\\private\\life\\movie\\WWDC_2010_keynote.m4v\r\n
------------------------------ab847ea8ba7a\r\n
Content-Disposition: form-data; name="filehash"\r\n
\r\n
fc884e136ada6a0d21cb22df64095850;bf11c971a439215af399213fa49fee02;3bbc3ecb4646f0e86bc9197eae2aed06;d96fe613346c17d345ecc723318e1b1d\r\n
------------------------------ab847ea8ba7a\r\n
Content-Disposition: form-data; name="vhash"\r\n
\r\n
f85c68ce0c9b811ac9a700af3ba2fbf6\r\n
------------------------------ab847ea8ba7a\r\n
Content-Disposition: form-data; name="shortname"\r\n
\r\n
wwdc 2010 keynote\r\n
------------------------------ab847ea8ba7a--\r\n

raw post data
'POST /api/subapi.php HTTP/1.0\r\nUser-Agent: SPlayer Build 1476\r\nHost: www.shooter.cn\r\nAccept: */*\r\nContent-Length: 655\r\nContent-Type: multipart/form-data; boundary=----------------------------ab847ea8ba7a\r\n\r\n'
>>> t1=c.read()
>>> t1
'------------------------------ab847ea8ba7a\r\nContent-Disposition: form-data; name="pathinfo"\r\n\r\nD:\\private\\life\\movie\\WWDC_2010_keynote.m4v\r\n------------------------------ab847ea8ba7a\r\nContent-Disposition: form-data; name="filehash"\r\n\r\nfc884e136ada6a0d21cb22df64095850;bf11c971a439215af399213fa49fee02;3bbc3ecb4646f0e86bc9197eae2aed06;d96fe613346c17d345ecc723318e1b1d\r\n------------------------------ab847ea8ba7a\r\nContent-Disposition: form-data; name="vhash"\r\n\r\nf85c68ce0c9b811ac9a700af3ba2fbf6\r\n------------------------------ab847ea8ba7a\r\nContent-Disposition: form-data; name="shortname"\r\n\r\nwwdc 2010 keynote\r\n------------------------------ab847ea8ba7a--\r\n'



import urllib,urllib2
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

register_openers()

from fetchsub import *

fpath = r"D:\private\life\movie\WWDC_2010_keynote.m4v"
pathinfo = fpath.encode("UTF-8")
filehash = genFileHash(fpath)
shortname = getShortName(fpath)
datagen, headers = multipart_encode({'pathinfo':pathinfo, 'filehash':filehash, 'shortname':shortname})
headers['User-Agent']='SPlayer Build 1476'
theurl = "http://splayer1.shooter.cn/api/subapi.php"
req = urllib2.Request(theurl, datagen, headers)
handle = urllib2.urlopen(req)


result:
1       SubPackage count(loop)
    4       Package Data Length
    4       Desc Data Length(iDescLength)
    iDescLength     Desc Data
    4       File Data Length
    1       File count(loop)
        4       File Pack Length
        4       File Ext Name Length(iExtLength)
        iExtLength      File Ext Name
        4       File Data Length

why can not get sub files of some video? is there some difference between request sent by splayer.exe and my request?
capture these package.
trace splayer.exe


>>> c.read(1024)
POST /api/subapi.php HTTP/1.0\r\n
User-Agent: SPlayer Build 1543\r\n
Host: www.shooter.cn\r\n
Accept: */*\r\n
Content-Length: 655\r\n
Content-Type: multipart/form-data; boundary=----------------------------5620852ec052\r\n
\r\n
------------------------------5620852ec052\r\n
Content-Disposition: form-data; name="pathinfo"\r\n
\r\n
D:\\private\\life\\movie\\WWDC_2010_keynote.m4v\r\n
------------------------------5620852ec052\r\n
Content-Disposition: form-data; name="filehash"\r\n
\r\n
fc884e136ada6a0d21cb22df64095850;bf11c971a439215af399213fa49fee02;3bbc3ecb4646f0e86bc9197eae2aed06;d96fe613346c17d345ecc723318e1b1d\r\n
------------------------------5620852ec052\r\n
Content-Disposition: form-data; name="vhash"\r\n
\r\n
c9f705092bf506a73f3fb6e28320cb35\r\n
------------------------------5620852ec052\r\n
Content-Disposition: form-data; name="shortname"\r\n
\r\n
wwdc 2010 keynote\r\n
------------------------------5620852ec052--\r\n


hashlib.md5("SP,aerSP,aer %d &e(\xd7\x02 %s %s%s"%(1543, "D:\\private\\life\\movie\\WWDC_2010_keynote.m4v", "fc884e136ada6a0d21cb22df64095850;bf11c971a439215af399213fa49fee02;3bbc3ecb4646f0e86bc9197eae2aed06;d96fe613346c17d345ecc723318e1b1d","\x00")).hexdigest()


hashlib.md5("SP,aerSP,aer %d &e(\xd7\x02 %s %s"%(1543, "D:\\private\\life\\movie\\WWDC_2010_keynote.m4v", "fc884e136ada6a0d21cb22df64095850;bf11c971a439215af399213fa49fee02;3bbc3ecb4646f0e86bc9197eae2aed06;d96fe613346c17d345ecc723318e1b1d")).hexdigest()
"""
import sys,os
import hashlib
from httplib import HTTPConnection, OK

import struct
from cStringIO import StringIO
import gzip
import traceback
import random
from urlparse import urlparse

SVP_REV_NUMBER = 1543
CLIENTKEY = "SP,aerSP,aer %d &e(\xd7\x02 %s %s"
RETRY = 3

def grapBlock(f, offset, size):
    f.seek(offset)
    return f.read(size)

def getBlockHash(f, offset):
    return hashlib.md5(grapBlock(f, offset, 4096)).hexdigest()

def genFileHash(fpath):
    ftotallen = os.stat(fpath).st_size
    if ftotallen < 8192:
        return ""
    offset = [4096, ftotallen/3*2, ftotallen/3, ftotallen - 8192]
    f = open(fpath, "rb")
    return ";".join(getBlockHash(f, i) for i in offset)

def getShortNameByFileName(fpath):
    fpath = os.path.basename(fpath).rsplit(".",1)[0]
    fpath = fpath.lower()
    
    for stop in ["blueray","bluray","dvdrip","xvid","cd1","cd2","cd3","cd4","cd5","cd6","vc1","vc-1","hdtv","1080p","720p","1080i","x264","stv","limited","ac3","xxx","hddvd"]:
        i = fpath.find(stop)
        if i >= 0:
            fpath = fpath[:i]
    
    for c in "[].-#_=+<>,":
        fpath = fpath.replace(c, " ")
    
    return fpath.strip()

def getShortName(fpath):
    for i in range(3):
        shortname = getShortNameByFileName(os.path.basename(fpath))
        if not shortname:
            fpath = os.path.dirname(fpath)
        else:
            return shortname

def genVHash(svprev, fpath, fhash):
    """
    the clientkey is not avaliable now, but we can get it by reverse engineering splayer.exe
    to get the clientkey from splayer.exe:
    f = open("splayer","rb").read()
    i = f.find(" %s %s%s")"""
    global CLIENTKEY
    if CLIENTKEY:
        #sprintf_s( buffx, 4096, CLIENTKEY , SVP_REV_NUMBER, szTerm2, szTerm3, uniqueIDHash);
        vhash = hashlib.md5(CLIENTKEY%(svprev, fpath.encode("UTF-8"), fhash.encode("UTF-8"))).hexdigest()
    else:
        #sprintf_s( buffx, 4096, "un authiority client %d %s %s %s", SVP_REV_NUMBER, fpath.encode("utf8"), fhash.encode("utf8"), uniqueIDHash);
        vhash = hashlib.md5("un authiority client %d %s %s "%(svprev, fpath.encode("UTF-8"), fhash.encode("UTF-8"))).hexdigest()
    return vhash

def urlopen(url, svprev, formdata):
    ua = "SPlayer Build %d" % svprev
    #prepare data
    #generate a random boundary
    boundary = "----------------------------" + "%x"%random.getrandbits(48)
    data = []
    for item in formdata:
        data.append("--" + boundary + "\r\nContent-Disposition: form-data; name=\"" + item[0] + "\"\r\n\r\n" + item[1] + "\r\n")
    data.append("--" + boundary + "--\r\n")
    data = "".join(data)
    cl = str(len(data))
    
    r = urlparse(url)
    h = HTTPConnection(r.hostname)
    h.connect()
    h.putrequest("POST", r.path, skip_host=True, skip_accept_encoding=True)
    h.putheader("User-Agent", ua)
    h.putheader("Host", r.hostname)
    h.putheader("Accept", "*/*")
    h.putheader("Content-Length", cl)
    h.putheader("Content-Type", "multipart/form-data; boundary=" + boundary)
    h.endheaders()
    
    h.send(data)
    
    resp = h.getresponse()
    if resp.status != OK:
        raise Exception("HTTP response " + str(resp.status) + ": " + resp.reason)
    return resp

def downloadSubs(fpath, lang):
    global SVP_REV_NUMBER
    global RETRY
    pathinfo = fpath.encode("UTF-8")
    if os.path.sep != "\\":
        #*nix
        pathinfo = "E:\\" + pathinfo.replace(os.path.sep, "\\")
    filehash = genFileHash(fpath)
    shortname = getShortName(fpath).encode("UTF-8")
    vhash = genVHash(SVP_REV_NUMBER, fpath, filehash)
    formdata = []
    formdata.append(("pathinfo", pathinfo))
    formdata.append(("filehash", filehash))
    if vhash:
        formdata.append(("vhash", vhash))
    formdata.append(("shortname", shortname))
    if lang != "chn":
        lang = lang.encode("UTF-8")
        formdata.append(("lang", lang))
    
    for server in ["www", "svplayer", "splayer1", "splayer2", "splayer3", "splayer4", "splayer5", "splayer6", "splayer7", "splayer8", "splayer9"]:
        for schema in ["http", "https"]:
            theurl = schema + "://" + server + ".shooter.cn/api/subapi.php"
            for i in range(1, RETRY+1):
                try:
                    print "trying %s (retry %d)" % (theurl, i)
                    handle = urlopen(theurl, SVP_REV_NUMBER, formdata)
                    resp = handle.read()
                    if len(resp) > 1024:
                        return resp
                    else:
                        print >> sys.stderr, "response data less than 1KiB, ignore"
                except Exception, e:
                    traceback.print_exc()
    raise Exception("can not download sub from server")

def getSub(fpath, lang):
    dirname = os.path.dirname(fpath)
    basename = os.path.basename(fpath)
    barename = basename.rsplit(".",1)[0]
    package = Package(StringIO(downloadSubs(fpath, lang)))
    i = 0
    for sub in package.SubPackages:
        for file in sub.Files:
            fn = os.path.join(dirname, ".".join([barename, lang, str(i), file.ExtName]))
            open(fn,"wb").write(file.FileData)
            i += 1
    
class Package(object):
    def __init__(self, s):
        self.parse(s)
    def parse(self, s):
        c = s.read(1)
        self.SubPackageCount = struct.unpack("!B", c)[0]
        print "self.SubPackageCount: %d"%self.SubPackageCount
        self.SubPackages = []
        for i in range(self.SubPackageCount):
            sub = SubPackage(s)
            self.SubPackages.append(sub)

class SubPackage(object):
    def __init__(self, s):
        self.parse(s)
    def parse(self, s):
        c = s.read(8)
        self.PackageLength, self.DescLength = struct.unpack("!II", c)
        self.DescData = s.read(self.DescLength).decode("UTF-8")
        c = s.read(5)
        self.FileDataLength, self.FileCount = struct.unpack("!IB", c)
        self.Files = []
        for i in range(self.FileCount):
            file = SubFile(s)
            self.Files.append(file)

class SubFile(object):
    def __init__(self, s):
        self.parse(s)
    def parse(self, s):
        c = s.read(8)
        self.FilePackLength, self.ExtNameLength = struct.unpack("!II", c)
        self.ExtName = s.read(self.ExtNameLength).decode("UTF-8")
        c = s.read(4)
        self.FileDataLength = struct.unpack("!I", c)[0]
        self.FileData = s.read(self.FileDataLength)
        if self.FileData.startswith("\x1f\x8b"):
            gzipper = gzip.GzipFile(fileobj=StringIO(self.FileData))
            self.FileData = gzipper.read()

def Usage():
    global USAGESTR
    print >>sys.stderr, USAGESTR

def main():
    #getopt sucks
    if len(sys.argv) == 2 and sys.argv[1] == "--help":
        Usage()
        return 0
    files = []
    try:
        i = iter(sys.argv[1:])
        while True:
            s = i.next()
            if s == "-l":
                lang = i.next()
            else:
                files.append(s)
    except StopIteration:
        lang = "chn"
    
    if not files:
        print >>sys.stderr, "No vide file specified"
        Usage()
        return 1
    for file in files:
        try:
            print "fetching sub file(s) for ", file
            getSub(os.path.abspath(file.decode(sys.stdin.encoding)), lang)
        except Exception,e:
            traceback.print_exc()
    return 0

if __name__ == "__main__":
    sys.exit(main())
