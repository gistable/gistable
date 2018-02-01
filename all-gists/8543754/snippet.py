#!/usr/bin/python

# # # # # # # # # # # # # # # # # # # #
#                                     #
# Script was made by Dennis           #
# http://stefansundin.com/blog/452    #
# http://pastebin.com/8cw9LHFg        #
#                                     #
# # # # # # # # # # # # # # # # # # # #
 
import urllib2, os, re

datadir = '/tmp/'
# this url has to be obtained by httpfox
playlist = 'http://www.youtube.com/api/manifest/hls_playlist/id/5iuHXO40V8Q.1/itag/93/source/yt_live_broadcast/ratebypass/yes/live/1/cmbypass/yes/newshard/yes/hls_chunk_host/www.youtube.com/gir/yes/dg_shard/5iuHXO40V8Q.1_93/pmbypass/yes/playlist_type/DVR/cp/U0hXR1VPVF9MTUNON19NSVhIOnV6eHhiQzBZU3lu/maudio/1/fexp/921071,916604,900504,914504,910207,929229,916623,929305,924616,924610,907231/upn/DXHc5N5ymUI/sver/3/cpn/nYSFeYBcBGtS35Ir/ip/2001:bb8:2002:3900:d6be:d9ff:fe4b:8c19/ipbits/48/expire/1382546773/sparams/ip,ipbits,expire,id,itag,source,ratebypass,live,cmbypass,newshard,hls_chunk_host,gir,dg_shard,pmbypass,playlist_type,cp,maudio/signature/24AB1330AB4161CDB1C9B8510F1A8A34A86D0AFB.98D4B116F56398B10E8A8BB1B9304CBF13F64FD9/key/dg_yt0/file/index.m3u8?start_seq='


for seq in xrange(0,100000):
    print "[+] Downloading playlist for seq %s..." % (seq)
    # skip if already exists
    if os.path.isfile(datadir+str(seq) + ".done"):
        print "[+] Sequence %s already done!" % (seq)
        continue
    response = urllib2.urlopen(playlist+str(seq))
    html = response.read()
    for line in html.split("\n"):
        if line.startswith("http://"):
            seq = re.search('/sq/(\d+)/file/', line).group(1)
            print "[+] Downloading video for sequence %s..." % (seq)

            # skip if already exists
            if os.path.isfile(datadir+str(seq) + ".done"):
                print "[+] Sequence %s already done!" % (seq)
                continue

            response = urllib2.urlopen(line)
            stream = response.read()
            f = open(datadir+str(seq)+'.asf', 'w')
            f.write(stream)
            f.close()
            f = open(datadir + str(seq) + ".done", 'w')
            f.write("")
            f.close()

# joining stream togeather in losless manner
# https://trac.ffmpeg.org/wiki/How%20to%20concatenate%20(join,%20merge)%20media%20files