#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk

import sys, os
import cStringIO
import base64
import json
import requests
import subprocess
from base64 import b64encode

client_id = "0d7cfd59581bfcb"
client_secret = "0f8983c9973adbcee07171a91e4cc60a1a63b61a"

headers = {"Authorization": "Client-ID " + client_id}

url = "https://api.imgur.com/3/upload"

def upload(img):
	
    fH = cStringIO.StringIO()
    img.save_to_callback(fH.write, "png")
	
    response = requests.post(url, headers = headers,
            data = {
                'key': client_secret,
                'image': b64encode(fH.getvalue()),
                'type': 'base64'
            })
    
    link = response.json()['data']['link']
    return link



def getImage():
    clipboard = gtk.clipboard_get()
    img = clipboard.wait_for_image()
    if img == None:
        subprocess.Popen(['notify-send', 'No image in clipboard'])
        sys.exit(0)
        
    return img
    
link = upload(getImage())

print link


os.popen('xsel -i -b', 'wb').write(link)
subprocess.Popen(['notify-send', 'Image uploaded', '--hint=int:transient:1'])
