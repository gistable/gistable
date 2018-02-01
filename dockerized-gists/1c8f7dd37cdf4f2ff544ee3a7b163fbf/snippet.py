#!/usr/bin/python

import xml.etree.ElementTree as ET
import requests
import uuid

params = {'cup2hreq': 'foo', 'cup2key': 'bar'}

platform = 'mac'
os_version = '10.12'
arch = 'x86_64h'
sp = '%s_%s' % (os_version, arch)
app_version = '53.0.2785.89'

xml = """
<request protocol="3.0" version="KeystoneAdmin-1.2.5.1190" ismachine="0" requestid="{%s}" dedup="cr" sessionid="{%s}" installsource="ondemandupdate"> 
        <os platform="%s" version="%s" arch="%s" sp="%s" />
        <app appid="com.google.Chrome" version="%s" cohort="1:1y5/f7r:" cohortname="51_mac_106" lang="en-us" installage="89" brand="GGRO" signed="1">
                <ping r="-1" rd="-2" />
                <updatecheck />
        </app>
</request>
""" % (str(uuid.uuid1()), str(uuid.uuid1()), platform, os_version, arch, sp, app_version)

r = requests.post('https://tools.google.com/service/update2', params=params, data=xml)

root = ET.fromstring(r.text)

dmg_url_list = []

for tag in root.iter('url'):
    print tag.attrib['codebase']
    dmg_url_list.append(tag.attrib['codebase'])
    break

for tag in root.iter('package'):
    print tag.attrib['name']
    dmg_url_list.append(tag.attrib['name'])

dmg_url = ''.join(dmg_url_list)    
print dmg_url
