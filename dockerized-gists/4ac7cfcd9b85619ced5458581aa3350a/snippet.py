# coding: utf-8

import requests
import os
import datetime
from lxml import etree

url = 'https://api.int.bbc.co.uk/pips/api/v1/clip/pid.p0002b84/'
cert = os.environ.get('CERT')
headers = {'Accept': 'application/xml'}
NSMAP = {'p': 'http://ns.webservices.bbc.co.uk/2006/02/pips'}

r = requests.get(url, cert=cert, headers=headers)

# convert the requests bytestream to an lxml Element (I call it an XML infoset)
infoset = etree.XML(r.content)

# find the long synopsis node
ls = etree.ElementTree(infoset).xpath('/p:pips/p:clip/p:synopses/p:synopsis[@length="long"]', namespaces=NSMAP)

# remove the long synopsis node
ls[0].getparent().remove(ls[0])

# create a new long synopsis node
ls = etree.Element("synopsis", length="long")
ls.text = str(datetime.datetime.now())

# find the synopses node
s = etree.ElementTree(infoset).xpath('/p:pips/p:clip/p:synopses', namespaces=NSMAP)

# append the long_synopsis to the synopses
s[0].append(ls)

r = requests.put(url, cert=cert, data=etree.tostring(infoset))

r = requests.get(url, cert=cert, headers=headers)

print(r.text)