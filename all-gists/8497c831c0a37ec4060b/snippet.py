#!/usr/bin/env python
#-----ButtonBot.py-----#
#                      #
# made by /u/J08nY     #
# v2.3                 #
#                      #
#----------------------#

from urllib import urlencode
import httplib
from websocket import create_connection
import re
from random import choice
import time
from calendar import timegm
from json import loads
import threading
import signal
import sys
from platform import system
import argparse

USER_AGENTS = ["Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
               "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",
               "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/33.0",
               "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
               "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
               "Opera/9.80 (Windows NT 6.1) Presto/2.12.388 Version/12.16",
               "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko"]

class ButtonBot(threading.Thread):
    """
    ButtonBot capable of listening on the WebSocket for the button ticks and
    click on a desired time.
    This bot also has a logging capability.
    
    Command-line parameters:
        -o outputEvery :output data collected every -o seconds
        -c clickTime :click button when it reaches -c seconds
        -u user :username to click the button with
        -p passwd :password to login
        -w wss :use this WebSocket address explicitly
        -q :output data on script interruption
    """
    
    WSS_PATTERN = re.compile('"wss://(.+?)"')
    MODHASH_PATTERN = re.compile('modhash": "(.+?)"')
    CFDUID_PATTERN = re.compile("__cfduid=(.+?);")
    SESSION_PATTERN = re.compile("reddit_session=(.+?);")
    
    endColor = "\033[0m"
    ranges = {(60,52):"\033[35m",#purple <60,52>
              (51,42):"\033[34m",#blue   <51,42>
              (41,32):"\033[32m",#green  <41,32>
              (31,22):"\033[33m",#yellow <31,22>
              (21,12):"\033[33m",#orange <21,12>
              (11,1):"\033[31m"} #red    <11,1>
    
    LOGIN_HEADER = {"Host":"www.reddit.com",
          "User-Agent":choice(USER_AGENTS),
          "Accept":"application/json, text/javascript, */*; q=0.01",
          "Accept-Language":"en-US,en;q=0.5",
          "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
          "X-Requested-With":"XMLHttpRequest",
          "Referer":"http://www.reddit.com/r/thebutton/",
          "Origin":"http://www.reddit.com",
          "Connection":"keep-alive",
          "Pragma":"no-cache",
          "Cache-Control":"no-cache"}

    SITELOAD_HEADER = {"Host":"www.reddit.com",
          "User-Agent":choice(USER_AGENTS),
          "Accept":"text/html, application/xhtml+xml, application/xml; q=0.9,*/*; q=0.8",
          "Accept-Language":"en-US,en;q=0.5",
          "Referer":"http://www.reddit.com/r/thebutton/",
          "Origin":"http://www.reddit.com",
          "Connection":"keep-alive",
          "Pragma":"no-cache",
          "Cache-Control":"no-cache"}

    CLICK_HEADER = {"Accept":"application/json, text/javascript, */*; q=0.01",
          "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
          "Origin":"http://www.reddit.com",
          "Referer":"http://www.reddit.com/r/thebutton",
          "User-Agent":choice(USER_AGENTS),
          "X-Requested-With":"XMLHttpRequest"}
    
    
    def __init__(self, clickTime=None, user=None, passwd=None, outputEvery=None, wss=None, outputOnStop=None):
        threading.Thread.__init__(self)

        self.clickTime = clickTime
        self.user = user
        self.passwd = passwd
        self.shouldClick = (self.clickTime != None) and (self.user != None) and (self.passwd != None)

        self.wss = wss
        self.outputEvery = outputEvery
        self.outputOnStop = outputOnStop
        
        self.tickCount = 0
        self.ticks = []
        self.running = False
        self.connected = False
        self.logged = False
        self.cookie = ""

        self.shouldColor = system() == "Linux"

    def run(self):
        print "START"
        self.running = True
        
        if self.shouldClick:
            self._login()
        if self.wss == None:
            self._getWss()
        
        self._connect()
        while self.running:
            tick = self._getTick()
            this = float(tick["payload"]["seconds_left"])

            if self.shouldClick:
                if this == self.clickTime:
                    self._click(this,tick["payload"]["now_str"],tick["payload"]["tick_mac"])
            
            #tickTime = time.time()
            #serverTime = timegm(time.strptime(tick["payload"]["now_str"],"%Y-%m-%d-%H-%M-%S"))
            #delta = round(abs(tickTime-serverTime),3)

            if self.tickCount > 0:
                last = self.ticks[-1]
                lastParticipants = int(last["payload"]["participants_text"].replace(",",""))
                thisParticipants = int(tick["payload"]["participants_text"].replace(",",""))
                if thisParticipants > lastParticipants:
                    print " Click" # + str(delta)
                else:
                    print "" #str(delta)

            if self.shouldColor:
                for rang, color in self.ranges.items():
                    if this <= rang[0] and this >= rang[1]:
                        print color,
                        break
            
            print str(this),
            if self.shouldColor:
                print self.endColor,

            self.ticks.append(tick)
            self.tickCount+=1
            
            if self.outputEvery != None and self.outputEvery != 0:
                if self.tickCount % self.outputEvery == 0  and self.tickCount != 0:
                    outputCount = self.tickCount/self.outputEvery
                    if outputCount > 1:
                        self.ticks = self.ticks[1:]
                    self.output()
                    self.ticks = self.ticks[-1:]
            

        self._disconnect()

        if self.shouldClick:
            self._logout()
        print "STOP"
            
    def _login(self):
        data = {"op":"login-main",
                "user":self.user,
                "passwd":self.passwd,
                "api_type":"json"}
        header = self.LOGIN_HEADER
        header["Content-Length"]=str(len(urlencode(data)))
        
        connection = httplib.HTTPConnection("www.reddit.com",80)
        connection.request("POST","/api/login/",urlencode(data),header)
        response = connection.getresponse()
        connection.close()
        
        if response.status != 200:
            raise Exception
        
        cookie = response.getheader("set-cookie")
        cfduid = self.CFDUID_PATTERN.search(cookie).group(1)
        reddit_session = self.SESSION_PATTERN.search(cookie)
        if type(reddit_session) == type(None):
            print "ACCOUNT CREDENTIALS ERROR?"
            self.shouldClick = False
            return
        else:
            reddit_session = reddit_session.group(1)
        self.cookie = "__cfduid=" + cfduid + "; reddit_session=" + reddit_session + ";"

        header = self.SITELOAD_HEADER
        header["Cookie"] = self.cookie

        connection = httplib.HTTPConnection("www.reddit.com",80)
        connection.request("GET","/r/thebutton",None,header)
        response = connection.getresponse()
        page = response.read()
        connection.close()
        
        if response.status != 200:
            raise Exception
        
        self.wss = self.WSS_PATTERN.search(page).group(1)
        self.modhash = self.MODHASH_PATTERN.search(page).group(1)
        if self.wss != None and self.modhash != None:
            self.logged = True
            print "LOGGED IN uh:" + self.modhash
            print "GOT WSS(logged)"
        else:
            raise Exception
        
    def _getWss(self):
        connection = httplib.HTTPConnection("www.reddit.com",80)
        connection.request("GET","/r/thebutton",None,self.SITELOAD_HEADER)
        response = connection.getresponse()
        page = response.read()
        connection.close()
        
        self.wss = self.WSS_PATTERN.search(page).group(1)
        print "GOT WSS"
        
    def _connect(self):
        self.sock = create_connection("wss://"+self.wss)
        self.connected = True
        print "WSS CONNECTED"

    def _getTick(self):
        result = self.sock.recv()
        return loads(result)

    def _click(self, seconds, now_str, tick_mac):
        if not self.logged:
            return
        data = {"seconds":str(int(seconds)),
                "prev_seconds":str(int(seconds)),
                "tick_time":now_str,
                "tick_mac":tick_mac,
                "r":"thebutton",
                "uh":self.modhash,
                "renderstyle":"html"}
        header = self.CLICK_HEADER
        header["Content-Length"] = str(len(urlencode(data)))
        header["Cookie"] = self.cookie
        
        connection = httplib.HTTPConnection("www.reddit.com",80)
        connection.request("POST","/api/press_button",urlencode(data),header)
        connection.close()
        
        print "CLICKED ->" + str(int(seconds))
        
    def _disconnect(self):
        self.sock.close()
        self.connected = False
        print "WSS DISCONNECTED"

    def _logout(self):
        if not self.logged:
            return
        data = {"uh":self.modhash,
                "top":"off",
                "dest":"/r/thebutton"}
        header = self.SITELOAD_HEADER
        header["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        header["Content-Length"] = str(len(urlencode(data)))
        header["Cookie"] = self.cookie

        connection = httplib.HTTPConnection("www.reddit.com",80)
        connection.request("POST","/logout",urlencode(data),header)
        response = connection.getresponse()
        connection.close()
        
        if response.status != 302:
            print "DID NOT LOGOUT"
        else:
            self.logged = False
            print "LOGGED OUT"

    def stop(self):
        self.running = False

    def output(self):
        outTimeStart = time.time()
        
        startTime = time.strptime(self.ticks[0]["payload"]["now_str"],"%Y-%m-%d-%H-%M-%S")
        endTime = time.strptime(self.ticks[-1]["payload"]["now_str"],"%Y-%m-%d-%H-%M-%S")

        filename = "from" + time.strftime("%d_%m_%H-%M-%S",startTime) + "to" + time.strftime("%d_%m_%H-%M-%S",endTime)

        out = open(filename, "w")
        for data in self.ticks:
            tick = float(data["payload"]["seconds_left"])
            participants  = int(data["payload"]["participants_text"].replace(",",""))
            timeString = data["payload"]["now_str"]
            out.write(timeString + " " + str(participants) + " " + str(tick) + "\n")
        out.close()
        
        outTimeStop = time.time()
        print "OUTPUT " + filename + " output took " + str(outTimeStop - outTimeStart) + " seconds"

    def sigint(self, signal, frame):
        print "SIGINT"
        self.stop()
        if self.outputOnStop:
            self.output()
        sys.exit(0)

if __name__  == "__main__":
    parser = argparse.ArgumentParser(description="ButtonBot.py v2.0 made by /u/J08nY")
    parser.add_argument("-o",type=int,dest="outputEvery",
                        help="output data collected every -o seconds")
    parser.add_argument("-c",type=int,dest="clickTime",
                        help="click button when it reaches -c seconds")
    parser.add_argument("-u",dest="user",
                        help="username to click the button with")
    parser.add_argument("-p",dest="passwd",
                        help="password to login")
    parser.add_argument("-w",dest="wss",
                        help="use this WebSocket address")
    parser.add_argument("-q",action="store_true",dest="outputOnStop",
                        help="output data on script interruption")
    args = parser.parse_args()
    bot = ButtonBot(clickTime=args.clickTime,user=args.user,passwd=args.passwd,outputEvery=args.outputEvery,wss=args.wss,outputOnStop=args.outputOnStop)
    bot.start()
    signal.signal(signal.SIGINT, bot.sigint)
    if system() == "Linux":
        signal.pause()
    else:
        while True:
            time.sleep(1)
