#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import json
import requests
import scraperwiki

from collections import OrderedDict

def save_rows(row):
    scraperwiki.sqlite.save(
                unique_keys=['actor', 'actor2'],
                data=row,
                table_name="actors")

SUMMARY_TEMPLATE = OrderedDict({u'actor': None,
                                u'actor2': None,
                                u'numEvent': None,
                                u'comment': None})

names = ["David_Beckham", "Sepp_Blatter"]
query_string_template = "https://newsreader.scraperwiki.com/people_sharing_event_with_a_person/page/{page}?uris.0=dbpedia%3A{name}&output=json"
for name in names:
    for page in range(1,22):
        r = requests.get(query_string_template.format(name=name, page=page))
        try:
            actor_data = r.json()
        except:
            continue
        for entry in actor_data["payload"]:
            print name, page, entry["actor2"]
            save_rows(entry)
