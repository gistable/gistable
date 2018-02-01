"""
Created on June 19th, 2013. via. Sublime Text 2

@author: lurker
"""

#!/usr/bin/env python
# -*- coding: utf8 -*-

import urllib2,httplib
import string
import json
import requests
import re
import sys
import os

url_create='http://jing.fm/api/v1/sessions/create'
url_fetch_pls='http://jing.fm/api/v1/search/jing/fetch_pls'
url_fetch_track_infos='http://jing.fm/api/v1/music/fetch_track_infos'
url_surl = 'http://jing.fm/api/v1/media/song/surl'

fig_base_address = 'img.jing.fm/album/'

host="jing.fm"
payload={
"Host" :"jing.fm","Connection":"keep-alive","Content-Length":42, 
"X-Requested-With":"XMLHttpRequest",
"Referer":"http://jing.fm/","User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:13.0) Gecko/20100101 Firefox/13.0.1",
"Pragma":"no-cache",
"Cache-Control":"no-cache"}
init_headers ={
"Accept":"application/json, text/javascript, */*; q=0.01",
"Accept-Language":"en-us,en;q=0.5",
"Accept-Encoding":"gzip, deflate",
"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",}

email = 'test@gmail.com'
passwd = 'passwd'


class JingFM:
    def __init__(self,email, passwd):
		
        self.params_create = {'email':email,'pwd':passwd}
        self.resp_create = requests.post(url_create, data=json.dumps(payload), headers=init_headers,params=self.params_create)
        if self.resp_create.content.find('true') == -1:
                self.err_msg('canot log in')
        #token
        jath = self.resp_create.headers["jing-a-token-header"]
        jrth = self.resp_create.headers["jing-r-token-header"]
        self.headers = {
        "Accept":"application/json, text/javascript, */*; q=0.01",
        "Accept-Language":"en-us,en;q=0.5",
        "Accept-Encoding":"gzip, deflate",
        "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
        "jing-a-token-header": jath,
        "jing-r-token-header": jrth,}
        json_create = json.loads(self.resp_create.content)
        self.uid = json_create['result']['usr']['id']
            
    def err_msg(self, msg):
        print msg
        sys.exit()
    def fetch_pls(self, key):
        self.limit = 2;
        self.params_fetch_pls = {'mt':'','ps':self.limit, 'q':key,'ss':'true','st':0,'tid':0,'u':self.uid}
        self.resp_fetch_pls = requests.post(url_fetch_pls, headers = self.headers, params = self.params_fetch_pls)
        json_fetch_pls = json.loads(self.resp_fetch_pls.content)
        #only first song
        self.mid_group = []
        self.tid_group = []
        self.fid_group = []
        for i in xrange(self.limit):
                self.mid_group.append(json_fetch_pls['result']['items'][i]['mid']) 
                self.tid_group.append(json_fetch_pls['result']['items'][i]['tid'])
                fid = json_fetch_pls['result']['items'][i]['fid']
                addon = fid[0:4]+'/'+fid[4:8]+'/'+fid[8:10]+'/'+fid[10:12]+'/'
                #not true always
                self.fid_group.append(fig_base_address + 'AM'+'/'+addon + 'AM'+fid)
                    
    def fetch_track_infos(self):
        self.track_infos = []
        for i in xrange(self.limit):
                self.params_fetch_track_infos = {'tid':self.tid_group[i], 'uid':self.uid}
                self.resp_fetch_track_infos = requests.post(url_fetch_track_infos, headers = self.headers, params = self.params_fetch_track_infos).content
                self.track_infos.append(self.resp_fetch_track_infos)

    def surl(self):
        self.surl = []
        for i in xrange(self.limit):
                self.params_surl = {'mid':self.mid_group[i], 'type':'NO'}
                self.resp_surl = requests.post(url_surl,headers = self.headers, params = self.params_surl)
                json_surl = json.loads(self.resp_surl.content)
                self.surl.append(json_surl['result'])
        return self.surl
        #print self.fid_group
        #print self.track_infos
		
if __name__=="__main__":
        while(True):
		c=JingFM(email,passwd)
		c.fetch_pls('piano')
		c.fetch_track_infos()
	        song_list = c.surl()
		bashCommand = "mplayer -really-quiet "
		for x in range(len(song_list)):
			bashCommand = bashCommand + " " + song_list[x]
		bashCommand = bashCommand + " -loop 1"
		import subprocess
		process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
		output = process.communicate()[0]




