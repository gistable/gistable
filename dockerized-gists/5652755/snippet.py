#!/usr/bin/env python

"""
Download PyCon US 2012 videos in a multithreaded way.
Requirement: youtube-dl script.

written by Jabba Laci, 2013 (jabba.laci@gmail.com)
http://pythonadventures.wordpress.com/

PyCon US 2012 videos: http://pyvideo.org/category/17
youtube-dl: http://rg3.github.io/youtube-dl/

Usage:
======
1) download youtube-dl and put it somewhere in the PATH
2) create a subdirectory called "download"
3) launch this script

Total size of the videos is about 27.5 GB.
The download process can take several hours.
You can interrupt the downloading with "killall python".
If you re-launch the script, the downloading will resume.

Tested under Linux with Python 2.7.
"""

import os
from Queue import Queue
from threading import Thread, Lock

TO_DIR = "download"
THREADS = 10

lock = Lock()
q = Queue()
threads = []

DATA = ["AeQxx4zXd5Q", "O8WXXtDUUOE", "ktLyuWoRHH8", "tKTW8Jd0BlQ", "A3Qe5wUbXzM",
"ZwBiQEHS4T8", "Rmg4-Ae1P1o", "9XlPKEessD8", "MIAKOMzRl1I", "q_i3CHNITQ4",
"3CSxYKbxfPU", "4bWC_VXffq4", "v7HH_CNIdXc", "ziz2lh-14i8", "dhUo_lpD7v0",
"WMUXMqYhQ-M", "qLXllxd4Z1c", "3FcAcE3Zq2Q", "U1Y5Uxn2Rcw", "x-JDra36m38",
"Me9SZohibPQ", "KUOoStyV7Zs", "Qh4Gkkgi1Mw", "Hx6VxszpvsY", "CFt6QrzavH0",
"AMMBYLB3qd0", "fVpvd7OX6PQ", "OceCWIqZt7I", "VuFW0PkNS74", "5jRLjGWWaHs",
"_CPNLY_Gf7s", "67l4czkKsz8", "FCiA6e44aOI", "uUEwEMMCZhE", "cY7pE7vX6MU",
"vP6j7VDpPrI", "QrITN6GZDu4", "euh9ZQi339o", "EBRMq2Ioxsc", "3BYN3ouwkRA",
"tCUdeLIj4hE", "Wk8zAr0R9zQ", "NUQMr5R3dlk", "twQKAoq2OPE", "dJJDndQrsSw",
"Q0Q9K93bK-4", "5YQrFiWa50M", "VMIj6eB9baY", "KOfB5WQb39g", "M5IPlMe83yI",
"2gha47uSk5c", "lJL2asANiyM", "YHXX3KuB23Q", "LddeJ06JoXE", "gpKMwPoldak",
"BoMQqW0lxVE", "NkUTLRZBWLM", "fekA2mRGTTE", "b7R3-_ViNxk", "nhr-YErfW8k",
"WZoeqnsY9AY", "Wh9a0obtQUQ", "ahM4GBZ-6qg", "399c-ycBvo4", "kdZuUIj4lMo",
"E09qigk_hnY", "nvkCqFLtcJI", "NIcijUt-HlE", "l_HBRhcgeuQ", "dX3DRdFKW_E",
"y_cXzaymXm0", "RBOScqRGHZA", "QPgqfnKG_T4", "fWONoZvTi80", "sgHbC6udIqc",
"1CjX385y3e4", "hnhN2_TpY8g", "GxyfYEe8MiQ", "wslWYg0CTkY", "54XwSUC8klI",
"6wZoBbE-rOo", "Zv26xHYlc8s", "N4zdWLuSbV0", "H841U6RhrDU", "bwwf_HbEJQM",
"qmgh14LUOjQ", "qTwvObrRGdY", "Ycvg0PCQ-sM", "ickNQcNXiS4", "C9K8DOe1zWw",
"47NSfuuuMfs", "3UHE-zD1r_M", "bTXert2uRco", "Bt2HStzaBzE", "z1RQMm37Xmw",
"LnVkLXRIbIg", "P5ad6NpjR3M", "hyzPYaAmVOc", "tYW52SLy_w0", "JOXwclgvXB0",
"188mXjwdkak", "9G6-GksU7Ko", "TmuEDxX1FDQ", "jXlR0Icvvh8", "vfYul2E56fo",
"cSbD5SKwak0", "bGWytn-Ff9E", "hvPYuqzTPIk", "RAxiiRPHS9k", "Mv3xgBQJPaE",
"jOu0D9ttCFI", "4-TwdBuTR1A", "yflKOoAohEk", "ANhTacigaf8", "vfPtGsSJldg",
"YdnBK5yO4zU", "26wgEsg9Mcc", "R9ITLdmfdLI", "KUpIFhNW89A", "OBbvj0WWT-g",
"9q8LTZSvpr8", "qbYYamU42Sw", "-Mx1JVTFOBY", "AZDWveIdqjY", "__s45TTXxps",
"QGfxLXoMpPk", "3dMq_3UUPxg", "9LVqBQcFmyw", "Adr_QuDZxuM", "YyEReiAYGlU",
"G-lGCC4KKok", "1VZfL9JVgFg", "n6145JSeqWc", "XGF3Qu4dUqk", "Xu5EhKVZdV8",
"o9pEzgHorH0", "miGolgp9xq8", "Xk6gQ6s2QjU", "tYk4_Nzl-Gg", "sdkAXM36C7M",
"L-fXOoxrt0M", "Iw9-GckD-gQ", "xHqlzuPq_qQ", "duc3jYgAaR0", "Zd5dfooZWG4",
"g0CankXpFZg", "ULdDuwf48kM", "P7SVi0YTIuE", "Pi9NpxAvYSs", "qgGqaBAEy3Q",
"bobeo5kFz1g", "w26x-z-BdWQ", "t_ziKY1ayCo", "Bs6-sai1fKE", "oZw8m_lyhvo",
"hp5ymCrD9yw", "2G5YTlheCbw", "SULKL7TMRsU", "Thd8yoBou7k", "52wxGESwQSA",
"NBSosX8xiRk"]


def read_urls():
    global q
    #
    for yid in DATA:
        q.put("https://www.youtube.com/watch?v={yid}".format(yid=yid))


class DownLoadThread(Thread):
    def __init__(self, thread_id):
        super(DownLoadThread, self).__init__()
        self.thread_id = thread_id

    def run(self):
        global q
        #
        while not q.empty():
            url = q.get()
            cmd = "youtube-dl {url} -t -c 1>/dev/null".format(url=url)
            with lock:
                print "{tid}: START {cmd}".format(tid=self.thread_id, cmd=cmd)
                print "# queue size:", q.qsize()
            os.system(cmd)
            with lock:
                print "{tid}: STOP {cmd}".format(tid=self.thread_id, cmd=cmd)


def main():
    global threads
    #
    read_urls()
    #
    os.chdir(TO_DIR)
    #
    for i in xrange(THREADS):
        t = DownLoadThread(i)
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print "# END"

#############################################################################

if __name__ == "__main__":
    main()
