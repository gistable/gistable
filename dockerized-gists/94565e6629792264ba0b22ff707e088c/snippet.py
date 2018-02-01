#!/usr/bin/env python
#coding:utf-8
# Author:  Sg4Dylan --<sg4dylan#gmail.com>
# Purpose: A simple script to download video from Bilibili
# Created: 08/07/2016

import sys
from subprocess import call

def check_and_go(args):
    try:
        if not (args[0] and args[1]):
            usage_tip(0)
        if "index" in args[0]:
            usage_tip(2)
        else:
            if args[1] == 0:
                usage_tip(2)
            else:
                bilibili_down_them_all(args[0],int(args[1]))
    except IndexError:
        usage_tip(0)
    except ValueError:
        usage_tip(1)

def bilibili_down_them_all(link,p_count):
    for i in range(1,p_count+1):
        print("Start downloading...\n%s\n" % link)
        call("you-get -d " + link + "index_" + str(i) + ".html", shell=True)

def usage_tip(exit_flag):
    if exit_flag == 0:
        print("Missing parameters !\n")
    else:
        print("Please check you parameters !\n")
    print("Usage: python bilibili_download_them_all.py [PageLink] [VideoCount]")
    print("Example: python bilibili_download_them_all.py http://www.bilibili.com/video/av4432868/ 9")
    sys.exit(exit_flag)

if __name__ == "__main__":
    check_and_go(sys.argv[1:])