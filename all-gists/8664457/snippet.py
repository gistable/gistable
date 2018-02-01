#!/usr/bin/env python

import os
import requests
import libxml2
import time
import phue
import daemon
import lockfile
import signal

trigger_apps = ["Plex/Chromecast"]
sleep_interval = 10

class Chromecast(object):
    apps_url = "http://%s:8008/apps/"

    def __init__(s, device_name):
        s.device_name = device_name

    def runningApp(s):
        try:
            response = requests.get(s.apps_url % s.device_name, timeout=2.0)
            data = libxml2.parseDoc(response.text)

            context = data.xpathNewContext()
            context.xpathRegisterNs("root", "urn:dial-multiscreen-org:schemas:dial")
            context.xpathRegisterNs("cast", "urn:chrome.google.com:cast")

            description = context.xpathEval("//cast:description")

            return description[0].content
        except:
            return "None"

class Hue(object):
    def __init__(s, device_name):
        s.device_name = device_name
        s.bridge = phue.Bridge(device_name)
        s.bridge.connect()
        s.dimmed = False

    def dimUp(s):
        s.dimmed = False
        for light in s.lights:
            s.bridge.set_light(light['id'], {'transitiontime':20,'on':True,'bri':light['bri'],'hue':light['hue'],'sat':light['sat']})

    def dimDown(s):
        s.dimmed = True
        s.lights = []
        for light in s.bridge.lights:
            s.lights.append({'id':light.light_id,'hue':light.hue,'on':light.on,'bri':light.brightness,'sat':light.saturation})

        s.bridge.set_light([2,3], {'transitiontime':20,'on':False})
        s.bridge.set_light(1, {'transitiontime':20,'on':True,'bri':1,'hue':65535,'sat':255})

def cleanup():
    if hue.dimmed:
        hue.dimUp()

chromecast = Chromecast("chromecast")
hue = Hue("philips-hue")

context = daemon.DaemonContext(pidfile = lockfile.FileLock(os.path.join(os.environ['HOME'], ".chromelight")))
context.signal_map = {
    signal.SIGTERM: cleanup,
    signal.SIGHUP: 'terminate'
}

context.stdout = open(os.path.join(os.environ['HOME'], '.chromelight.log'), 'w+')
context.stderr = context.stdout

with context:
    while True:
        app = chromecast.runningApp()
        print "Running:", app

        if app in trigger_apps:
            if not hue.dimmed:
                hue.dimDown()
                print "Dimming down"
        elif hue.dimmed:
            hue.dimUp()
            print "Dimming up"

        time.sleep(sleep_interval)
