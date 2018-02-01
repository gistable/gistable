#!/usr/bin/python3

import os
import re
import json
import pickle
from bs4 import BeautifulSoup
import requests
from time import strftime

t = strftime('%m-%d-%y, %H:%M')
devices = {"ryu": "Pixel C", "angler": "Nexus 6P", "bullhead": "Nexus 5X", "shamu": "Nexus 6", "fugu": "Nexus Player",
           "volantisg": "Nexus 9 (LTE)", "volantis": "Nexus 9 (Wi-Fi)", "hammerhead": "Nexus 5", "razor": "Nexus 7 [2013] (Wi-Fi)",
           "razorg": "Nexus 7 [2013] (Mobile)"}

chantags = {"ryu": "pixelcimages", "angler": "n6pimages", "bullhead": "n5ximages", "shamu": "n6images", "fugu": "nplayerimages",
            "volantisg": "n9lteimages", "volantis": "n9wifiimages", "hammerhead": "n5images", "razor": "n72013wifiimages",
            "razorg": "n72013mobileimages"}

if os.path.isfile("/home/username/scripts/log/nimglog"):
    f = open("/home/username/scripts/log/nimglog", 'at')
else:
    f = open("/home/username/scripts/log/nimglog", 'wt')

basepath = "/home/username/scripts/currentversion/"

# get current page, save in tree
page = requests.get('https://developers.google.com/android/nexus/images')
soup = BeautifulSoup(page.text, 'lxml')

vsre = re.compile('(\([\dA-Z]{6}\))')
dnre = re.compile('("[a-zA-Z]+")')
data = {}

for device in soup.find_all("h2", id=True)[1:]:
    device_name = device.get_text(strip=True)
    device_name = dnre.search(device_name).groups(1)[0]
    device_name = device_name.replace('"', '')

    # continue
    if device_name not in devices:
        continue

    data[device_name] = [version.find("td").get_text(strip=True)
                         for version in device.find_next("table").find_all("tr", id=True)]


for dname in data:
    curversion = ""
    pathn = basepath + dname
    if os.path.isfile(pathn):
        g = open(pathn, 'rb')
        curversion = pickle.load(g).lower()
        g.close()

    fullstr = data[dname][-1]
    vstring = vsre.search(fullstr).groups(1)[0]
    vstring = vstring.replace("(", "").replace(")", "").lower()

    if curversion == vstring:
        f.write(t + ': same | ' + dname + '\n')
        continue

    pushurl = 'https://api.pushbullet.com/v2/pushes'
    headers = {'Authorization': 'Bearer APIKEY', 'Content-Type': 'application/json'}
    payload = {'channel_tag': chantags[dname], 'type': 'link', 'title': devices[dname] + ' Factory Image Released',
               'body': 'A new factory image, ' + fullstr + ', for the ' + devices[dname] + ' has been released.',
               'url': 'https://developers.google.com/android/nexus/images'}

    r = requests.post(pushurl, headers=headers, data=json.dumps(payload))

    if os.path.isfile(pathn):
        os.remove(pathn)

    g = open(pathn, 'wb')
    pickle.dump(vstring, g)
    g.close()
    f.write(t + ': CHANGE | ' + devices[dname] + ' | ' + curversion + '\n')

f.write("--------------------\n")
f.close()