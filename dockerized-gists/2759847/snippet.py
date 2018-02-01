#!/usr/bin/env python

import cStringIO
import json
import pycurl
import os
import sys

##########
# configuration
# list of jobs from jenkins, they are expected to be URL encoded already
jobList = [
    "job1"
    ,"job2"
]

build_host = "my_build_host"
lastBuildAPIURL = "http://" + build_host + "/job/%s/lastSuccessfulBuild/api/json"
lastBuildArtifactLURL = "http://" + build_host + "/job/%s/lastSuccessfulBuild/artifact/%s"
localSaveDir = "tmp"
artifactExtension=".jar"

##########
# UDFs

def downloadFile(url,filename):
    print "==> Downloading File: ",filename," URL: ",url
    fp = open(filename, "wb")
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEDATA, fp)
    curl.perform()
    curl.close()
    fp.close()


###########
# start

print "Fetching files from Jenkins"

if not os.path.exists(localSaveDir):
    print "==> Creating Dir %s" % (localSaveDir)
    os.makedirs(localSaveDir)

for job in jobList:
    buf = cStringIO.StringIO()
    jobURL = lastBuildAPIURL % (job)
    c = pycurl.Curl()
    c.setopt(c.URL, jobURL)
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.perform()
 
    jsonstr = buf.getvalue()
#    print jsonstr
    jd = json.loads(jsonstr)
#    print jd
    buf.close()
    artifacts = jd['artifacts']

    for art in artifacts:
        if art['fileName'].find(artifactExtension) > -1:
            artURL = lastBuildArtifactLURL % (job,art['relativePath'])
            downloadFile(str(artURL),localSaveDir + "/" + str(art['fileName']))

print "Done"
buf.close()
sys.exit(0)
