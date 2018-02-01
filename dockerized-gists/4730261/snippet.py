#!/usr/bin/env python

"""
This is mainly a demonstration of OCLC's experimental Worldcat Live API [1] 
from Python. You should be able to use this module like so:

  import worldcat_live

  for item in worldcat_live.items():
      print item["title"]

worldcat_live.items is a Python generator that will return recently cataloged
items, forever. Optionally pass in a poll_time to control how often to check 
the Worldcat Live API for more results (default is every 10 seconds).

If you run the module directly you'll see new titles as they are cataloged 
along with the name of the institution that cataloged them displayed on the 
console. Sometimes you may notice the organization being displayed as 
"None <None>" which is because WorldCat Live items are missing the instsym 
sometimes [2].

[1] http://experimental.worldcat.org/xwwg/
[2] https://twitter.com/edsu/status/299469915906244608
"""

import json
import time
import urllib
import datetime
import xml.etree.ElementTree as xml

base_url = "http://experimental.worldcat.org/xwwg/rest/feed?format=json" 


def items(poll_time=10):
    """A generator for new items added to Worldcat, it returns each item
    as a Python dictionary that maps to the JSON response from the Worldcat 
    Live API's JSON response.

    The poll_time is the number of seconds to wait before polling for more 
    results from the Worldcat Live API.

    It does annotate the response with information about the organization 
    that cataloged the item in the item's "org" key.
    """
    maxseq = None
    while True:
        url = base_url + "&start=seq-%s" % maxseq if maxseq else base_url
        response = json.loads(urllib.urlopen(url).read())

        for item in response["newrec"]:
            if not maxseq or item["id"] >= maxseq:
                # XXX remove this if we can rely on "title" being there
                if not item.has_key("title"): item["title"] = None
                item["org"] = get_org(item.get("instsym", None))
                item["url"] = "http://worldcat.org/oclc/" + item["oclcno"]
                item["created"] = datetime.datetime.fromtimestamp(float(item["created"]))
                yield item

        maxseq = response["maxseq"]
        time.sleep(poll_time)

orgs = {} 
def get_org(org_code):
    """looks up a OCLC institution symbol and returns a dictionary of
    information about that organization using the Worldcat Registry API.
    """
    if not org_code: return {"name": None, "url": None}
    if orgs.has_key(org_code): return orgs[org_code]

    url = "http://www.worldcat.org/webservices/registry/lookup/Institutions/oclcSymbol/%s?serviceLabel=content" % org_code
    doc = xml.fromstring(urllib.urlopen(url).read())

    org = {} 
    org["name"] = doc.findtext(".//{info:rfa/rfaRegistry/xmlSchemas/institutions/nameLocation}institutionName")
    org["url"] = doc.findtext(".//{info:rfa/rfaRegistry/xmlSchemas/institutions/nameLocation}infoSiteUrl")
    orgs[org_code] = org
    return org


if __name__ == "__main__":
    for item in items():
        print "[%s] %s <%s> %s <%s>" % (item["created"], item["org"]["name"], item["org"]["url"], item["title"], item["url"])
