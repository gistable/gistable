#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Deepak.G.R."
__license__ = 'Public Domain'

"""
usage:
Go to command line and type

python ai-class.py "topic-name"

topic-names can be "Welcome to AI", "Problem Solving"

PS: Python 2.7.2 should be installed in your system.

Let me know if you get into any problems.
"""
from xml.etree import ElementTree as ET
from urllib import *
from urlparse import *
from sgmllib import SGMLParser
import os
from json import *
import re
import pdb
import sys
import json
import urllib2


code = 35
"""
code = 34 for 640*360
code = 35 for 854*480(Default)
code = 22 for 1270*720
"""
if code == 22:
    video_fmt = '.mp4'
else:
    video_fmt = '.flv'
    
url_youtube = 'http://www.youtube.com/watch?v='
quiz_hash = dict();

req_unit = sys.argv[1]

class UrlLister(SGMLParser):
    
    def reset(self):
        SGMLParser.reset(self)
        self.urls = []
        self.flag = 0;
        self.req_unit = req_unit;
        self.names = [];
    
    def start_a(self, attrs):
        href = [value for name, value in attrs if name == 'href']
        topic = re.search(r'/course/topic/(\d)+', str(href[0]))
        
        if topic:
            self.flag = 0

        match = re.search(r'/course/video/\w+/\d+$', str(href[0]))
        
        if match and self.flag == 1:
            category = [value for name, value in attrs if name == 'id']
            
            if 'quiz' in category[0]:
                quiz_id = re.findall(r'quiz_(\d+)', category[0])[0]
                video_ids = quiz_hash[quiz_id]
                for video_id in video_ids:
                    link = url_youtube + video_id
                    self.urls.append(link)
            else:
                video_id = re.findall(r'video_\d+_(.+)', category[0])[0]
                link = url_youtube + video_id
                self.urls.append(link)
            
    def handle_data(self, text):
        if self.flag == 0:
            text = text.strip();
            text = re.sub(r'[^A-Za-z]', '', text).lower()
            self.req_unit = re.sub(r'[^A-Za-z]', '', self.req_unit).lower()
            if text == self.req_unit and len(text) != 0:
                self.flag = 1
            
class youtubeSub:
    def __init__(self):      
        self.srt_string = list()
        self.title = ''
        
    def time_format(self, secs):
        hrs = 0
        mins = 0
        parts = str(secs).split('.')
        secs = int(parts[0])
        msecs = parts[1]

        if secs >= 60:
            mins = mins + (secs/60)
            secs = secs % 60
            
        if mins >= 60:
            hrs = hrs + (mins/60)
            mins = mins % 60      
        return (hrs, mins, secs, msecs)

    def store_line(self, line, hrs, mins, secs, msecs):
        h = '%02d' % hrs
        m = '%02d' % mins
        s = '%02d' % secs
        ms = msecs + '0' * (3-len(msecs))
        self.srt_string.append(h + ':' + m + ':' + s + ',' + ms)

    def parse_data(self, data):
        try:
            tree = ET.fromstring(data)
        except:
            return

        line = 1                
        for subelement in tree:
            time = subelement.attrib        
            secs = float(time['start'])
            t_secs = secs
            (hrs, mins, secs, msecs) = self.time_format(secs)
            self.srt_string.append(str(line) + '\n')  
            self.store_line(line, hrs, mins, secs, msecs)
            self.srt_string.append(' --> ')      
            dur = float(time['dur'])
            secs = t_secs + dur
            (hrs, mins, secs, msecs) = self.time_format(secs)
            self.store_line(line, hrs, mins, secs, msecs)
            self.srt_string.append('\n' + subelement.text + '\n\n')
            line = line + 1
        self.write_sub()
            
    def write_sub(self):
        dirname = 'subtitles'
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        os.chdir(dirname)
        fobj = open(self.title, 'w')
        for line in self.srt_string:
            fobj.write(line.encode('ASCII', 'ignore'))
        fobj.close()
        os.chdir('..')

    def get_subtitle(self, get_vars):
        self.title = get_vars['title'][0] + '.srt'
        try:
            sub_link = get_vars['ttsurl'][0] + '&'\
                       + 'expire=' + get_vars['expire'][0] + '&'\
                       + 'key=' + get_vars['key'][0] + '&'\
                       + 'format=1' + '&'\
                       + 'hl=en' + '&'\
                       + 'ts=' + get_vars['timestamp'][0] + '&'\
                       + 'v=' + get_vars['video_id'][0] + '&'\
                       + 'lang=en' + '&'\
                       + 'type=track' + '&'\
                       + 'name=English via dotsub' + '&'\
                       + 'kind=&asr_langs=en,ko,ja&caps=asr' + '&'\
                       + 'signature=' + get_vars['signature'][0]
        except:
            return          
        data = urlopen(sub_link).read()
        self.parse_data(data)
        
def init_quiz_hash():
    print 'STATUS: Initializing quiz_id hash'
    quiz_url = 'http://www.ai-class.com/course/json/filter/QuizQuestion'
    quiz_url = urllib2.urlopen(quiz_url);
    data = json.load(quiz_url)
    quiz_id = list()

    for ind in xrange(len(data['data'])):
        piece = str(data['data'][ind])
        match = re.search(r'\'quiz_question\': (\d+?),', piece)
        v_id = re.findall(r'\'youtube_id\': u\'(.+?)\'', piece)
        
        hw = re.search(r'\'is_homework\': u\'true', piece)
        if match and v_id:
            q_id = match.group(1)
            
            for v in v_id:
                if not quiz_hash.has_key(q_id):
                    quiz_hash[q_id] = list()

                quiz_hash[q_id].append(v)

    print 'STATUS: quiz_id Initialized.'

def download_video(urls):
    dirname = str(req_unit)
    
    if os.path.exists(dirname):
        delete_recent_video(dirname)
    else:
        os.mkdir(dirname)
        os.chdir(dirname)
    
    for video_url in urls:
        video_id = parse_qs(urlparse(video_url).query)['v'][0]
        get_vars = parse_qs(unquote(urlopen("http://www.youtube.com/get_video_info?video_id=" + video_id).read()))
        title = get_vars['title'][0] + video_fmt
        
        if os.path.isfile(title):
            continue
        
        i = 0
        entries = get_vars['itag']
        for entry in entries:
            match = re.search(r'.*itag=' + str(code), entry)
            if match:
                break
            i = i + 1
            
        if not match:
            print 'ERROR: Couldn\'t Download video: ', title
            continue

        link = get_vars['itag'][i]
        link = re.findall(r'\d+,url=(.*)', link)[0]

        print '\n-->Downloading, Title: ', title
        urlretrieve(link, title)
        sub_obj = youtubeSub()
        sub_obj.get_subtitle(get_vars)

    os.chdir('..')

def delete_recent_video(dirname):
    os.chdir(dirname)
    files = os.listdir('.')
    if not files:
        return
    
    name = ''
    recent = 0
    for fo in files:
        if os.path.isdir(fo):
            continue
        temp = os.stat(fo).st_mtime
        if temp > recent:
            recent = temp
            name = fo
    os.remove(name)

def main():
    
    init_quiz_hash();
    page = urllib2.urlopen("http://www.ai-class.com/home/")
    htmlSource = page.read()
    parser = UrlLister()
    print 'STATUS: Fetching video urls.'
    parser.feed(htmlSource)
    print 'STATUS: SUCCESS'
    page.close()
    parser.close()
    print 'Number of videos: ', len(parser.urls);
    print 'STATUS: Starting download.'
 
    download_video(parser.urls)
    
    print '\n\n*********Download Finished*********'
    
if __name__  == "__main__":
    main()
