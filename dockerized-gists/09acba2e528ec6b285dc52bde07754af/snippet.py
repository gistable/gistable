# if netid is logged in, send a random cat fact to all of its terminals.
# usage: crontab -e. paste in:
#       0 * * * * python ~/catfact.py
# logs in ~/victims.txt
# why did i spend so much time on this.
# this got me banned from the school servers for two days
messagechance = 5 # 1 is 1%, 99 is 99%. keep in mind this will only run if they're logged in.
postscript = '\n this has been an automated cat fact. contact me to unsubscribe. or to subscribe others.\n'
listofnetids = ['netids','go','here']

import os
import subprocess
import random

from time import gmtime, strftime

# catfacts
import requests
import json
catfact = json.loads(requests.get('http://catfacts-api.appspot.com/api/facts').content)["facts"]
#catfact = requests.get('http://catfacts-api.appspot.com/api/facts').json()["facts"] # this is an attempt to not use the json li$

FNULL = open(os.devnull, 'w')

who = subprocess.check_output(['who']) # 2.7 compliant
listwho = who.split('\n')

for netid in listofnetids:
        if random.randint(1,100) >= messagechance:
                continue # to the next netid
        print(netid+" won the diceroll!")
        ptslist = []
        for line in listwho:
                if netid in line:
                        ptslist.append(line.split(' ')[1])
        if not ptslist: #if pts is empty
                continue # they're not online, diceroll next netid
        for pts in ptslist:
                p = subprocess.Popen(['write',netid,pts],stdout=FNULL,stdin=subprocess.PIPE)
                p.stdin.write(' '+catfact[0]+postscript)
                p.stdin.close()
        with open("victims.txt","a") as f:
                f.write(netid+', '+catfact[0]+' '+strftime("%Y-%m-%d %H:%M:%S", gmtime())+'\n')
