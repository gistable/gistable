# -*- coding: utf-8 -*- 
import os
import urllib2
import urllib
import json
import logging
import time
import sys
import lxml.html as html
import re

def fromURL(url):
    return re.search(r"(?:http://)?(\w+).tumblr.com/post/(\d+).+", url, re.U | re.M | re.L | re.I).groups()

def getNotesKey(user, noteid):
    text = urllib2.urlopen("http://%s.tumblr.com/post/%s" % (user, noteid)).read()
    result = re.search(r"/notes/(\d+)/(\w+)\?from\_c=(\d+)", text, re.U | re.M | re.L | re.I)
    return text, result.groups()

def getNotes(user, noteid, note_load_id, from_c=0):
    text = urllib2.urlopen("http://%s.tumblr.com/notes/%s/%s?from_c=%s" % (user, noteid, note_load_id, from_c)).read().decode('utf-8')

    fromc_match = re.search(r"/notes/\d+/\w+\?from\_c=(\d+)", text, re.U | re.M | re.L | re.I)
    fromc = -1
    if fromc_match is not None:
        fromc = fromc_match.groups()[0]

    return html.fromstring(text), fromc

def notes(user, noteid):
    text, (postid, postkey, fromc) = getNotesKey(user, noteid)
    ret = []

    fromc = 0
    while fromc != -1:
        ol, fromc = getNotes(user, noteid, postkey, fromc)
        
        for li in ol:
            if li.get('class', "") is None:
                continue
            if li.get('class', "").find("more_notes_link_container") == -1:
                ret.append(li)
    
    return ret

def main(url):
    def prittyfy(li):
        for r in li.findall("blockquote"):
            li.remove(r)
        return li.text_content().strip()
    
    posts = notes(*fromURL(url))
    for li in posts:
        print prittyfy(li)

if __name__ == '__main__': 
    if len(sys.argv) != 2:
        print "useage: tublrnotes.py url"
    else:
        main(sys.argv[1])
