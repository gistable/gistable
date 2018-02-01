#!/usr/bin/python

import sys
import libvirt
from xml.etree.ElementTree import *

host = sys.argv[1]
conn = libvirt.open("qemu+tcp://%s/system" % host)

vms = []

ids = conn.listDomainsID()
for id in ids:
    dom = conn.lookupByID(id)
    vms.append(dom.name())

domains = conn.listDefinedDomains()
for domain in domains:
    vms.append(domain)

for vm in vms:
    print vm
    dom  = conn.lookupByName(vm)
    desc = fromstring(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
    desc.find(".//clock").set("offset", "localtime")
    conn.defineXML(tostring(desc))
