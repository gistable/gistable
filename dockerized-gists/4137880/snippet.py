#!/usr/bin/env python
import simplejson
import logging
import random
import re
import datetime
import string
import time
import sys
import urllib
import xmlrpclib
import base64
import os
import json
from flask import Flask, Request, Response
from werkzeug.routing import BaseConverter
import urllib2
from urllib import quote, unquote, urlencode
import argparse
from os import path
from urlparse import parse_qs
from urllib2 import URLError

class VideoInfo(object):
    def __init__(self, video_url):
        request_url = 'http://www.youtube.com/get_video_info?video_id='
        if 'http://www.youtube.com/watch?v' in parse_qs(video_url).keys():
            request_url += parse_qs(video_url)['http://www.youtube.com/watch?v'][0]
        elif 'v' in parse_qs(video_url).keys():
            request_url += parse_qs(video_url)['v'][0]
        request = urllib2.Request(request_url)
        try:
            self.video_info = parse_qs(urllib2.urlopen(request).read())
        except URLError :
            pass

def video_file_urls(videoinfo):
    url_encoded_fmt_stream_map = videoinfo.video_info['url_encoded_fmt_stream_map'][0].split(',')
    entrys = [parse_qs(entry) for entry in url_encoded_fmt_stream_map]
    url_maps = [dict(url=entry['url'][0]+'&signature='+entry['sig'][0], type=entry['type']) for entry in entrys]
    return url_maps
    
def GetYoutubeUrlMp4_1(url_str):
    video_info = VideoInfo(url_str)
    video_url_map = video_file_urls(video_info)
    url = ''
    for entry in video_url_map:
        entry_type = entry['type'][0]
        entry_type = entry_type.split(';')[0]
        if entry_type.lower() == 'video/mp4':
            url = entry['url']
            break
    return url

def GetYoutubeUrlMp4_Last(url_str):
    video_info = VideoInfo(url_str)
    video_url_map = video_file_urls(video_info)
    url = ''
    for entry in video_url_map:
        entry_type = entry['type'][0]
        entry_type = entry_type.split(';')[0]
        if entry_type.lower() == 'video/mp4':
            url = entry['url']
    return url     

application = app = Flask('wsgi')

@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('error.html'), 404)
    resp.headers['X-Something'] = 'A value'
    return resp

@app.route('/aaa2')
def welcome():
    return GetYoutubeUrlMp4_1("http://www.youtube.com/watch?v=DXFEYNH1pLc")
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

@app.route('/jpg1/<regex(".*"):filename>')
def FetchJPG1(filename):
    import StringIO
    output = StringIO.StringIO()

    content1 = GetYoutubeUrlMp4_1("http://www.youtube.com/watch?v=" + filename)
    response1 = urllib2.urlopen(content1, timeout=80)
    buff_size = 64000000
    while True:
        buffer = response1.read(buff_size)
        if not buffer:
            break
        output.write(buffer)

    contents = output.getvalue()
    return Response(contents, content_type="video/mp4")


@app.route('/jpg5/<regex(".*"):filename>')
def FetchJPG5(filename):
    import StringIO
    output = StringIO.StringIO()

    content1 = GetYoutubeUrlMp4_Last("http://www.youtube.com/watch?v=" + filename)
    response1 = urllib2.urlopen(content1, timeout=80)
    buff_size = 64000000
    while True:
        buffer = response1.read(buff_size)
        if not buffer:
            break
        output.write(buffer)

    contents = output.getvalue()
    return Response(contents, content_type="video/mp4")

@app.route('/nbcnightlynews')
def RawFetchMSNBCNightly():
    thisUrl = "http://podcastfeeds.nbcnews.com/audio/podcast/MSNBC-Nightly.xml"
    content = u""
    try:
        result = urllib2.urlopen(thisUrl)
        content = result.read()
        content = content.replace("enclosure url=\"", "enclosure url=\"http://xx.xx.af.cm/mp3/")
    except:
        pass
    return Response(content, content_type="text/xml")     

@app.route('/businessenglishpod')
def RawFetchBEP():
    thisUrl = "http://feeds2.feedburner.com/BusinessEnglishPod"
    content = u""
    try:
        result = urllib2.urlopen(thisUrl)
        content = result.read()
        content = content.replace("enclosure url=\"", "enclosure url=\"http://xx.xx.af.cm/mp3/")
    except:
        pass
    return Response(content, content_type="text/xml")   

@app.route('/env')
def env():
    return os.environ.get("VCAP_SERVICES", "{}")

if __name__ == '__main__':
    app.run(debug=True)
