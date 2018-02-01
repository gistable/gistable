# Ventriloquist - Build 0.1
# insert a dummy dsig table with unique numbers into .otf fonts
# the idea is to kill two birds with one stone
# this idea needs lots of testing
# to do: add SerialDump[] to a txt file for record keeping
# 
# jackson@okaytype.com

from fontTools.ttLib import TTFont
from mojo.compile import *
from robofab.interface.all.dialogs import GetFolder
import os
import datetime
from time import sleep
from os.path import exists

# number of serials to generate
packageNos=1

# notification center, so you can get coffee
def notify(title, subtitle, message):
    from os import system
    t = '-title {!r}'.format(title)
    s = '-subtitle {!r}'.format(subtitle)
    m = '-message {!r}'.format(message)
    a = '-sender {!r}'.format("com.typemytype.robofont")
    system('terminal-notifier {}'.format(' '.join([m, t, s, a])))
    
if exists("/usr/bin/terminal-notifier"):
    use_notifications = True
else:
    use_notifications = False
    print "In order to use notifications, install the command line program with:"
    print "$ sudo gem install terminal-notifier"

# make up the serials, based on the time
SerialDump=[]
for x in range(0, packageNos):
    b = "1"+datetime.datetime.now().strftime("%m%d%H%M%S%f")
    b = b[:-1]
    sleep(0.01)
    SerialDump.append(b)
    
# cull list to just .otf files
def collectSources(root):
    files = []
    ext = ['.otf']
    names = os.listdir(root)
    for n in names:
        if os.path.splitext(n)[1] in ext:
            files.append(os.path.join(root, n))
    return files

# set target folder
def makeDestination(root, z):
    macPath = os.path.join(root, 'Serialized', z)
    if not os.path.exists(macPath):
        os.makedirs(macPath)
    return macPath

# insert table into temp xml file
def seriaLize(savetemp, q):
    xbefor = '</ttFont>'
    xafter = '  <DSIG>\n    <tableHeader flag="0x1" numSigs="1" version="1"/>\n    <SignatureRecord format="1">\n'+q+'\n    </SignatureRecord>\n  </DSIG>\n\n</ttFont>'
    ttxf = open(savetemp, 'r')
    ttxfread = ttxf.read()
    ttxf.close()
    ttxfreplaced = ttxfread.replace(xbefor, xafter)
    ttxf = open(savetemp, 'w')
    ttxf.write(ttxfreplaced)
    ttxf.close()

# iterate through selected files
def doStuff(f):
    if f is not None:        
        # cut f to just .otf files
        paths = collectSources(f)

        for x in range(0, len(SerialDump)):
            currentNo = str(SerialDump[x])
            makeDestination(f, currentNo)
            
            for i in paths:
                
                instanceFolder, instanceName = os.path.split(i)    
                q = TTFont(i)
                
                serialfolder = instanceFolder + "/Serialized/" + currentNo + "/"
                savetemp =  serialfolder + instanceName + "-" + currentNo + ".ttx"
                savetemp = savetemp.replace(".otf", "")
                newfile = serialfolder + instanceName.replace(".otf", ".ttx")
                q.saveXML(savetemp)

                seriaLize(savetemp, currentNo)

                os.rename(savetemp, newfile)
                stderr, stdout = executeCommand(['ttx', newfile])
                os.remove(newfile)

                #print i, "finished serializing as", currentNo

# select fonts
f = GetFolder("Select Folder")

# run shit
doStuff(f)

notify("Ventriloquist is Done", "", "Check your output folders")
