#!/usr/bin/env python

import json, os, subprocess, sys, urllib2

from termcolor import cprint
from xml.dom import minidom

def abort(error):
    cprint(error, color='red', file=sys.stderr)
    exit(1)

def fetchMedias(videoId):
    jsonURL = "http://www.tsr.ch/?format=json/video&id=%s" % videoId
    jsonData = urllib2.urlopen(jsonURL).read()
    result = json.loads(jsonData)
    try:
        media = result["video"]["JSONinfo"]["media"]
        media = map(lambda m: m["url"].split("?")[0], media)
        baseURL = result["video"]["JSONinfo"].get("download") # was previously "http://media.tsr.ch/xobix_media/"
    except:
        abort("Media not found")
    
    try:
        tv = result["video"]["JSONinfo"]["streams"]["tv"]
        if tv.startswith(baseURL):
            tv = tv[len(baseURL):]
        media.append(tv)
    except:
        pass 
    
    return (media, baseURL)

def fetchCommand(media, baseURL):
    akastreamingPrefix = "http://akastreaming.tsr.ch/ch/"
    if media.startswith(akastreamingPrefix):
        mediaPath = media[len(akastreamingPrefix):]
        fileName = os.path.splitext(os.path.split(mediaPath)[1])[0] + ".flv"
        tokenURL = "http://www.rts.ch/token/ch-vod.xml?stream=media"
        try:
            dom = minidom.parse(urllib2.urlopen(tokenURL))
            #cprint(dom.toxml(), 'cyan')
        except:
            abort("Could not get token")
        
        hostname = dom.getElementsByTagName("hostname")[0].firstChild.data
        appName = dom.getElementsByTagName("appName")[0].firstChild.data
        authParams = dom.getElementsByTagName("authParams")[0].firstChild.data
        
        return ["rtmpdump", "--protocol", "rtmp", "--host", hostname, "--port", "1935", "--app", "%s?ovpfv=2.1.7&%s" % (appName, authParams), "--playpath", "mp4:media/" + mediaPath, "--flashVer", "MAC 10,1,102,64", "--swfUrl", "http://www.tsr.ch/swf/player.swf", "--pageUrl", "http://www.tsr.ch/video/", "--flv", fileName]
    else:
        return ["curl", "--verbose", "--location", "--remote-name", baseURL + media]

def main():
    if len(sys.argv) != 2:
        abort("usage: %s videoId" % sys.argv[0])
    
    medias, baseURL = fetchMedias(sys.argv[1])
    if len(medias) > 1:
        cprint("Which media do you want to download?")
        i = 1
        for m in medias:
            cprint("%u. %s" % (i, os.path.basename(m)))
            i = i + 1
        
        n = raw_input()
        try:
            n = int(n)
        except:
            n = len(medias)
        
        media = medias[n - 1]
    else:
        media = media[0]
    
    command = fetchCommand(media, baseURL)
    subprocess.call(command)
    fileName = os.path.split(command[-1])[-1]
    if os.path.splitext(fileName)[1] == ".flv":
        subprocess.call(["ffmpeg", "-i", fileName, "-vcodec", "copy", "-acodec", "copy", os.path.splitext(fileName)[0] + ".mp4"])
    
if __name__=='__main__':
    main()
