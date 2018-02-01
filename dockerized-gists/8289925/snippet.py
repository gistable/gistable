import os

'''

The command "deluge-console info" generates this output:

/home/pi$ deluge-console info

Name: Some video file
ID: 670b10e3842dfe57bedbd0653b09f0548034cbbb
State: Seeding Up Speed: 4.9 KiB/s
Seeds: 0 (745) Peers: 38 (3255) Availability: 0.00
Size: 1.9 GiB/1.9 GiB Ratio: 0.729
Seed time: 0 days 05:30:39 Active: 0 days 12:04:20
Tracker status: publicbt.com: Announce OK

Name: This DVD image
ID: 99cacefe03f0e12a085fb95b97c78b47aa266f4e
State: Downloading Down Speed: 49.0 KiB/s Up Speed: 419.1 KiB/s ETA: 17h 54m
Seeds: 11 (11) Peers: 4 (26) Availability: 11.85
Size: 4.9 GiB/8.0 GiB Ratio: 1.132
Seed time: 0 days 00:00:00 Active: 2 days 02:52:40
Tracker status: publicbt.com: Announce OK
Progress: 62.15% [#####################################~~~~~~~~~~~~~~~~~~~~~~]


This output is then parsed, and only active downloading torrents are shown:

 $ sudo python torrent-info.py

8.0G This DVD image
62% 61Kbps 14h3m
===

It contains the following information:
[Total size] [Torrent name]
[Completed %] [Download speed] [ETA]

'''
p = os.popen("su - deluge-user -c \"deluge-console info\"") #deluge-user is a username with access to deluge-console
q = p.read()
p.close()
r = q.split(" \n");

for torrent in r:
    if (torrent.find("State: Downloading") >= 0):
        s = torrent.split("\n")
        name = s[0][6:]
        down = s[2][31:]
        down = down[:down.find("/s Up")]
        down = down.split(" ")
	down = str(int(float(down[0]))) + down[1]
        eta = s[2][s[2].find("ETA: ")+5:]
        total = s[4]
        total = total[total.find("/") + 1:]
        total = total[:total.find(" Ratio")]
	total = total.replace("iB","").replace(" ","")
        percent = s[7][10:]
	percent = percent[:percent.find(" ")].replace("%","")
	percent = str(int(float(percent))) + "%"
        summary = "%s | %sbps | %s" % (percent, down, eta)
        summary = summary.replace("iB","").replace(" ","").replace("|"," ")
        print total + " " + name
        print summary
        print "==="