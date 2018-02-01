#! /usr/bin/env python3.2
"""
mozreplcurl - Wrapper around curl that adds on firefox's cookies, and updates firefox's cookie db after curl finishes running.

To update firefox's cookies db when firefox is running, mozrepl is required to be installed.
"""
import sys
import re
from telnetlib import Telnet
from argparse import ArgumentParser
from tempfile import mkstemp
import subprocess
from collections import namedtuple
import os
from urllib.parse import urljoin
from http.cookies import SimpleCookie

"""
2 ways: mozrepl or cookies.sqlite

If we modify cookies.sqlite we use the cookie-jar
option of curl instead. 

cookies.sqlite schema

CREATE TABLE moz_cookies (id INTEGER PRIMARY KEY, baseDomain TEXT, name TEXT, value TEXT, host TEXT, path TEXT, expiry INTEGER, lastAccessed INTEGER, creationTime INTEGER, isSecure INTEGER, isHttpOnly INTEGER, CONSTRAINT moz_uniqueid UNIQUE (name, host, path));
CREATE INDEX moz_basedomain ON moz_cookies (baseDomain);

lastAccessed and creationTime is in terms of 
PRTime (https://developer.mozilla.org/en/docs/PRTime)

PRTime is a 64-bit integer representing the number
of microseconds since the NSPR epoch

a.k.a int(time.time() * (10 ** 6))

"""

class MozRepl(object):
    def __init__(self, host="127.0.0.1", port=4242):
        self.host = host
        self.port = port
    
    def __enter__(self):
        #Start Telnet
        self.t = Telnet(self.host, self.port)
        #Wait for Prompt, and detect repl name at the same time
        _, match, _ = self.t.expect([br'(repl\d*)> '], timeout = 250)
        if match is None:
            raise Exception('Timeout: Could not detect prompt')
        self._context = match.group(1)
        self.context = match.group(1).decode()
        self.prompt = match.group(0)
        return self
    
    def __exit__(self, type, value, traceback):
        self.t.close()
        del self.t
        
    def js(self, command, **kwargs):
        #TODO: look for .....> which would mean repl expects a continuation line 
        #(Then send a ; to abort and hopefully get an error)
        from json import dumps
        args = sorted([(k, v) for k, v in kwargs.items()])
        arglist = ",".join(["repl"] + [x[0] for x in args])
        argvalues = ",".join([self.context] + [dumps(x[1]) for x in args])
        cmd = "(function({}){{ {} }})({});".format(arglist, command, argvalues) 
        self.t.write(cmd.encode() + b"\n")
        x = self.t.read_until(self.prompt).decode('utf-8', errors = 'replace')
        return x[:-(len(self.prompt))]

Cookie = namedtuple("Cookie", 
        ("host", "path", "name", "value", "issecure",
            "ishttponly", "issession", "expiry")
        )
"""
host: The host or domain for which the cookie is set.
Presence of a leading dot indicates a domain cookie;
Otherwise, the cookie is treated as a non-domain cookie.

path: Path within the domain for which the cookie is valid.

name: cookie name

value: cookie data
"""

def parse_cookiefile(contents:str) -> [Cookie]:
    """
    Each line has the format:

    DOMAIN\tNOTSESSIONCOOKIE\tPATH\tSECUREFLAG\tEXPIRATION\tNAME\tVALUE

    where:
    DOMAIN is the domain
    NOTSESSIONCOOKIE is "TRUE" if the cookie is not a
    session cookie and "FALSE" if the cookie is a
    session cookie.
    PATH is the root path under the domain where the
    cookie is valid. If this is /, the cookie is valid
    for the entire domain.
    SECUREFLAG is either "TRUE" or "FALSE". Whether or
    not a secure connection (HTTPS) is required to read 
    the cookie.
    EXPIRATION is the unixtime where the cookie is set to
    expire.
    NAME is the name of the cookie
    VALUE is the cookie value.

    Lines starting with # are comments and should
    be ignored.
    Lines starting with #HttpOnly_ are NOT COMMENTS but
    instead denote HTTP-only cookies. The rest
    of the line should be parsed as above.
    For more info on Http-only cookies see
    http://msdn.microsoft.com/en-us/library/ms533046.aspx

    For more info on the file format see 
    http://xiix.wordpress.com/2006/03/23/mozillafirefox-cookie-format/
    """
    if isinstance(contents, str):
        contents = str.split("\n")
    cookies = []
    for x in contents:
        x = x.strip("\n")
        if x.startswith("#HttpOnly_"):
            #Httponly cookie
            ishttponly = True
            x = x[len("#HttpOnly_"):]
        elif x.startswith("#") or not x.strip():
            #Commented line or blank line
            continue
        else:
            ishttponly = False
        host, notsessioncookie, path, issecure, expiry, name, value = x.split("\t", 6)
        if notsessioncookie == "TRUE":
            issession = False
        else:
            issession = True
        if issecure == "TRUE":
            issecure = True
        else:
            issecure = False
        cookies.append(Cookie(host, path, name, value, issecure, ishttponly, issession, int(expiry)))
    return cookies


def parse_dumpfile(contents, url):
    """1. Must track the Location redirects!"""
    if isinstance(contents, str):
        contents = contents.split("\n")
    def block(lines):
        set_cookies = []
        location=None
        date=None
        for x in lines:
            x = x.strip("\n")
            if x.startswith("Date: "):
                date = x[len("Date: "):]
        assert(date)
        for x in lines:
            x = x.strip("\n")
            if x.startswith("Location: "):
                location = x[len("Location: "):]
            elif x.startswith("Set-Cookie: "):
                set_cookies.append(x[len("Set-Cookie: "):])
        return (set_cookies, date, location)
    blocks = []
    lines = []
    cookies = []
    for x in contents:
        x = x.strip("\n")
        if not x:
            #New block. Parse previous block
            if lines:
                blocks.append(lines)
            lines = []
        else:
            lines.append(x)
    if lines:
        blocks.append(lines)
    for x in blocks:
        cookiestrs, date, location = block(x)
        for y in cookiestrs:
            cookies.append((y, url, date))
        if location:
            #Set URL for next block
            url = urljoin(url, location)
    return cookies

def main(m):
    p = ArgumentParser()
    #Handle curl's cookie option
    p.add_argument("-b", "--cookie", dest="cookie",
            action="append", default=[])
    #Handle curl's cookie jar option
    p.add_argument("-D", "--dump-header", dest="dumpheader",
            action="append", default=[])
    args, rest = p.parse_known_args()
    if rest:
        url = rest[-1]
        del rest[-1]
    else:
        p.error("No URL supplied")
    after_args = []
    _, dump_path = mkstemp()
    if ("-c" not in rest) and ("--cookie-jar" not in rest):
        #No cookie jar set, so curl will not
        #retain cookies on Location redirects.
        #Thus, we put in our own dummy cookie jar
        _, cj_path = mkstemp()
        after_args.append("-c")
        after_args.append(cj_path)
    else:
        cj_path = None
    #Get cookies from MozRepl
    cookies = m.js(r"""
    var ios = Components.classes["@mozilla.org/network/io-service;1"]
                .getService(Components.interfaces.nsIIOService);
    var uri = ios.newURI(url, null, null);
    var cookieSvc = Components.classes["@mozilla.org/cookieService;1"]
                  .getService(Components.interfaces.nsICookieService);
    var cookie = cookieSvc.getCookieStringFromHttp(uri, uri, null);
    repl.print(cookie)
    """, url=url).strip("\n")
    subprocess.call(["curl"] + rest + after_args + ["-b", cookies, "-D", dump_path, url])
    #Now read the cookiejar
    dump_f = open(dump_path, "r")
    dump_contents = dump_f.read()
    cookies = parse_dumpfile(dump_contents, url)
    dump_f.close()
    #Send those cookies to firefox
    for x in cookies:
        print(m.js(r"""
    var ios = Components.classes["@mozilla.org/network/io-service;1"]
                .getService(Components.interfaces.nsIIOService);
    var uri = ios.newURI(url, null, null);
    var cookieSvc = Components.classes["@mozilla.org/cookieService;1"]
                  .getService(Components.interfaces.nsICookieService);
    cookieSvc.setCookieStringFromHttp(uri, uri, null, cookiestr, date, null);
        """, url=x[1], cookiestr=x[0], date=x[2]))
    #Fetch our own
    #If cookiejar is not None, write tempfile
    #cookiejar to that cookiejar.
    #Remove cookiejar
    if args.dumpheader:
        f = open(args.dumpheader[-1], "w")
        f.write(dump_contents)
        f.close()
    os.remove(dump_path)
    if cj_path:
        os.remove(cj_path)

if __name__ == "__main__":
    with MozRepl() as m:
        main(m)