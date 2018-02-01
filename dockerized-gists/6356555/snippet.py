# Used for unshortening list of urls as wel as checking the HTTP status code of a webpage.
# When called from the command line, requires either a filename or STDIN as input
# Filename or standard input should contain one URL per line
# Output is printed to the standard out and saved to a JSON file using PickleDB.

__author__ = "Tim Hopper"
__email__ = "tdhopper@gmail.com"

import fileinput
import urllib2
import simplejson
import pickledb

UNSHORTME_API_KEY = ""
UNSHORTIT_API_KEY = ""
DB_LOCATION = 'unshort.db'
SAVE_EVERY_N = 100

def unshortme(url):
    query = "http://api.unshort.me/?r=" + url + "&t=json&api_key=" + UNSHORTME_API_KEY
    try:
        f = urllib2.urlopen(query)
        line = f.readline()
        return simplejson.loads(line)["resolvedURL"]
    except:
        return ""


def unshortenit(url):
    query = "http://api.unshorten.it?shortURL=" + url + "&apiKey=" + UNSHORTIT_API_KEY
    try:
        f = urllib2.urlopen(query)
        line = f.readline()
        return line
    except:
        return ""

def expand(url):
    g = unshortme(url)
    if g == "":
        g = unshortenit(url)
    return g

def get_status_code(host, path="/"):
    try:
        return urllib2.urlopen(x).getcode()
    except:
        return 0


def main():

    db = pickledb.load(DB_LOCATION, False)

    for i, url in enumerate(fileinput.input()):
        url = url.strip()
        
        if url == "" or db.get(url) != None:
            continue
        
        db.dcreate(url)
        db.dadd(url, ("unshort", expand(url)))
        db.dadd(url, ("status", get_status_code(url)))

        print i, url, db.dget(url, "unshort"), "[status:", db.dget(url, "status"), "]"

        if i % SAVE_EVERY_N == 0:
            db.dump()


if __name__ == '__main__':
    main()
