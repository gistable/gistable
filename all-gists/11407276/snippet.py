#!/usr/bin/env python
# -*- coding: utf-8 -*-
# glenn@sensepost.com
# Get times for a bus from TFL
from bs4 import BeautifulSoup
import requests
import re
import os

"""
Example:
$ python busStatus.py 55323
Route   Direction       Due (mins)
190     West Brompton   7
430     Sth Kensington  15
74      Baker St Stn    15
430     Sth Kensington  19
430     Sth Kensington  20
74      Sth Kensington  24
190     West Brompton   26
"""

class busStatus():
    def __init__(self,route):
        self.url = "http://accessible.countdown.tfl.gov.uk/arrivals/"
        self.route = route
        self.last_update = 0    #Use a monotonic clock to update times between refreshes
        self.buses = []
        self.update_buses()

    def get_buses(self):
        now = int(os.times()[4])
        mins_since_update = int(round((now - self.last_update) / 60.0))
        return [ (t[0], t[1], max(t[2] - mins_since_update, 0)) for t in self.buses]

    def update_buses(self):
        req = requests.get("%s%d" %(self.url,self.route))
        if req and req.status_code == 200:
            self.last_update = int(os.times()[4])
            soup = BeautifulSoup(req.text)
            routes, dirs, dues = [], [], []
            for r in soup.findAll("td", { "class" : "resRoute" }):
                route = int(r.text.strip())
                routes.append(route)
            for r in soup.findAll("td", { "class" : "resDir" }):
                dir = r.text.strip()
                dirs.append(dir)
            for r in soup.findAll("td", { "class" : "resDue" }):
                due = r.text.strip()
                if "due" in due:
                    due = "0 min"
                due = re.sub(' min', '', due)
                try:
                    due = int(due)
                except:
                    due = "-1"
                dues.append(due)
            self.buses = []
            for b in range(len(routes)):
                self.buses.append([routes[b], dirs[b], dues[b]])


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print "Please supply me a bus station ID."
        exit(-1)
    tt = busStatus(int(sys.argv[1]))
    tt.update_buses()
    buses = tt.get_buses()
    print "Route\tDirection\tDue (mins)"
    for bus in buses:
        print "%d\t%s\t%d" % (bus)