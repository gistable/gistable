#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import json
import requests
import scraperwiki

from collections import OrderedDict

def save_rows(row):
    scraperwiki.sqlite.save(
                unique_keys=['event', 'datetime'],
                data=row,
                table_name="events")

SUMMARY_TEMPLATE = OrderedDict({u'event': None,
                                u'event_size': None,
                                u'datetime': None})

names = ["Mohammed_bin_Hammam"]
query_string_template = "https://newsreader.scraperwiki.com/summary_of_events_with_actor/page/{page}?uris.0=dbpedia%3A{name}&output=json"
#query_string_template = "https://newsreader.scraperwiki.com/actors_sharing_event_with_an_actor/page/{page}?uris.0=dbpedia%3A{name}&output=json"
for name in names:
    for page in range(1,1000):
        r = requests.get(query_string_template.format(name=name, page=page))
        try:
            actor_data = r.json()
        except:
            continue
        for entry in actor_data["payload"]:
            print name, page, entry["event"]
            save_rows(entry)
