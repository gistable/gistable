#!/usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'ihciah'
# cid_hash_file function from https://github.com/binux/lixian.xunlei/blob/master/libs/tools.py
# Gist: https://gist.github.com/ihciah/30eda05ca36ee9f9f190067538b0ae04

import hashlib
import inotify.adapters
import os
import sys
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry
import re
import logging


class SubtitleDownloader:
    video_types = [u'mkv', u'mp4', u'avi', u'rm', u'rmvb', u'wmv', u'webm', u'mpeg', u'mpe', u'flv', u'3gp', u'mov']
    subtitle_types = [u'ass', u'srt', u'sub', u'sst', u'son', u'ssa', u'smi', u'tts', u'psb', u'pjs', u'stl', u'vsf']
    download_count = 3
    max_retries = 3
    watch_dir = b'/hdd/downloads'

    @staticmethod
    def url_get(url):
        s = requests.Session()
        retry = Retry(total=3, method_whitelist=frozenset(['GET', 'POST']))
        s.mount(u"http://", requests.adapters.HTTPAdapter(max_retries=retry))
        return s.get(url)

    @staticmethod
    def download_srt(subtitle_url, video_base_path, video_name, num):
        dot = subtitle_url.rfind(u'.')
        if dot < 0:
            return
        subtitle_type = subtitle_url[dot + 1:].lower()
        if subtitle_type not in SubtitleDownloader.subtitle_types:
            return
        srt_file = os.path.join(video_base_path, video_name + u'.%d.' % num + subtitle_type)
        if os.path.isfile(srt_file):
            return
        response = SubtitleDownloader.url_get(subtitle_url)
        if response.status_code == 200:
            with open(os.path.join(video_base_path, video_name + u'.%d.' % num + subtitle_type), 'wb') as f:
                f.write(response.content)

    @staticmethod
    def cid_hash_file(path):
        h = hashlib.sha1()
        size = os.path.getsize(path)
        with open(path, 'rb') as stream:
            if size < 0xF000:
                h.update(stream.read())
            else:
                h.update(stream.read(0x5000))
                stream.seek(size//3)
                h.update(stream.read(0x5000))
                stream.seek(size-0x5000)
                h.update(stream.read(0x5000))
        return h.hexdigest().upper()

    @staticmethod
    def fetch_subtitle_list(cid):
        patten = re.compile(b'surl="(.*?)"')
        url_base = u'http://subtitle.kankan.xunlei.com:8000/submatch/%s/%s/%s.lua'
        r = SubtitleDownloader.url_get(url_base % (cid[:2], cid[-2:], cid)).content
        srt_urls = patten.findall(r)[:SubtitleDownloader.download_count]
        return list(map(lambda url: url.decode(u'utf-8'), srt_urls))

    @staticmethod
    def download_subtitle(video):
        logging.debug(u"Processing: %s" % video)
        if not video:
            logging.error(u"Video file or dir does not exist. (%s)" % video)
            return -1
        if os.path.isdir(video):
            if sys.version_info.major == 2:
                code = sys.getfilesystemencoding()
                map(lambda path: SubtitleDownloader.download_subtitle(os.path.join(video, path.decode(code))),
                    os.listdir(video))
            else:
                list(map(lambda path: SubtitleDownloader.download_subtitle(os.path.join(video, path)),
                         os.listdir(video)))
            return
        if not os.path.isfile(video):
            logging.error(u"Video file does not exist. (%s)" % video)
            return -1
        video_base_path, video_filename = os.path.split(os.path.abspath(video))
        if not video_base_path or not video_filename:
            logging.error(u"Something error... (%s)" % video)
            return -1
        dot = video_filename.rfind(u'.')
        if dot < 0:
            logging.info(u"Not a video file. (%s)" % video_filename)
            return -1
        video_name = video_filename[:dot]
        video_type = video_filename[dot+1:]
        if video_type.lower() not in SubtitleDownloader.video_types:
            logging.info(u"Not a video file. (%s)" % video)
            return -2
        cid = SubtitleDownloader.cid_hash_file(video)
        subtitle_list = SubtitleDownloader.fetch_subtitle_list(cid)
        if not subtitle_list:
            logging.info(u"No subtitle available on the server.")
        else:
            logging.info(u"Fetching %d subtitles." % len(subtitle_list))
        for num, subtitle in enumerate(subtitle_list):
            SubtitleDownloader.download_srt(subtitle, video_base_path, video_name, num)
        logging.info(u"Done.")

    @staticmethod
    def inotify_loop():
        try:
            i = inotify.adapters.InotifyTree(SubtitleDownloader.watch_dir, mask=inotify.constants.IN_DELETE)
            for event in i.event_gen():
                if event is not None:
                    try:
                        (header, type_names, watch_path, filename) = event
                        filename = filename.decode('utf-8')
                        watch_path = watch_path.decode('utf-8')
                        if 'IN_DELETE' in type_names and filename.endswith(u'.aria2'):
                            video_filename = filename[:filename.rfind(u'.')]  # But this maybe a folder!
                            SubtitleDownloader.download_subtitle(os.path.join(watch_path, video_filename))
                    except:
                        pass
        except:
            pass

if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    SubtitleDownloader.inotify_loop()
