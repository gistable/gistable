import os
import re
import urllib2
import sys
import time


while True:      
        archive = urllib2.urlopen("http://pastebin.com/archive")
        u = []

        if not os.path.exists("pastebins"):
                os.mkdir("pastebins")
        try:
                f = open("pastebins/latest", "r")
                latest = f.read()
                f.close()
        except:
                latest = "none"
        print "Latest:", latest

        for l in archive:
                try: 
                        r = re.match("(.*)<td class=\"icon\"><a href=\"/(........)\">(.*)", l).group(2)
                        if r != latest:
                                u.append(r)
                        else:
                                break
                except:
                        pass

        if len(u) < 1:
                time.sleep(10)
                continue


        f = open("pastebins/latest", "w")
        f.write(u[0])
        f.close()

        brk=False
        founds = 0
        print "Downloading", len(u), "items"
        for r in u:
                        print "Downloading", r
                        try:
                                n = urllib2.urlopen("http://pastebin.com/raw.php?i=" + r).read()
                        except:
                                continue
                        for line in n:
                                for arg in sys.argv[1:]:
                                        if arg in line:
                                                print "FOUND!", arg, "in", r
                                                f = open("pastebins/"+ arg + "-" + r, "w")
                                                f.write(n)
                                                f.close()
                                                founds += 1
                                                brk = True
                                if brk:
                                        brk = False
                                        break
                        time.sleep(0.5)

        if founds > 0:
                os.system("kdialog --passivepopup \" Found " + str(founds) + " interesting pastebins\" 5")
        time.sleep(10)
