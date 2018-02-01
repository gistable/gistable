#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" """

import json
from urllib2 import urlopen
from lxml.html import document_fromstring
from lxml.cssselect import CSSSelector as cs

url = "http://www.livescores.com"

def strip(string):
    return string.strip().strip(u'\xa0')

def get_scores(text):
    doc = document_fromstring(text)
    trs = cs("table table table[bgcolor=\"#666666\"] tr")(doc)
    trs = [tr for tr in trs if tr.text_content()]

    ret = {}
    group = None

    for tr in trs:
        if group is None:
            group = strip(tr.text_content().strip())
            ret[group] = {}
            continue
        if not ret[group]:
            ret[group]["updated"] = strip(tr.text_content())
        elif len(tr) == 4:
            ret[group].setdefault("scores", []).append(
                {
                    "time": strip(tr[0].text_content()),
                    "home": strip(tr[1].text_content()),
                    "away": strip(tr[3].text_content()),
                    "score": strip(tr[2].text_content()),
                })
        else:
            group = strip(tr.text_content())
            ret[group] = {}
    return ret

def genjson():
    resp = urlopen(url)
    scores = get_scores(resp.read())
    print json.dumps(scores, indent=4)

if __name__ == '__main__':
    genjson()