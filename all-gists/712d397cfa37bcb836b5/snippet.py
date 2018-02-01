#!/usr/bin/env python

import os
import urllib2


countries={'DK':'denmark'}

os.system("/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper begin")
for country in countries.keys():
    url = "http://www.ipdeny.com/ipblocks/data/aggregated/%s-aggregated.zone" % country.lower()
    os.system("/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper delete firewall group network-group %s" % countries[country])
    os.system("/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set firewall group network-group %s" % countries[country])
    for ip in urllib2.urlopen(url).readlines():
        os.system("/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set firewall group network-group %s network %s" % (countries[country],ip))
os.system("/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper commit")
os.system("/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper end")


