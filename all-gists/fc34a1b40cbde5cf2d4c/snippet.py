#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Скрипт для скачивания музыки с сайта vkontakte.ru (vk.com)

Запуск:
python vkcom_audio_download.py

Принцип работы:
Скрипт проверяет сохраненный access_token. Если его нет или срок истек,
то открывается страница в браузере с запросом на доступ к аккаунту.
После подтверждения идет редирект на https://oauth.vk.com/blank.htm#... .
Нужно скопировать весь url, на который вас редиректнуло и вставить его
в консоль скрипта.
Далее будут скачиваться все ваши аудиозаписи. Если аудиозапись уже есть на
диске - то скачивания не происходит.

Будут запрошены ваши данные приложением с app_id = 3358129
Можно создать свое Standalone-приложение с доступом к аудио здесь:
http://vk.com/editapp?act=create
И заменить APP_ID на ваше.

Оригинальный скрипт https://gist.github.com/st4lk/4708673
Добавлены гринлеты, для лучшей нагрузки
(оригинал на моей выборке работал 32 минуты, модифицированный 7)
"""

import webbrowser
import pickle
import json
import urllib
import urllib2
import HTMLParser
import re
import os
import urlparse
from datetime import datetime, timedelta
import gevent
import gevent.monkey
from gevent.queue import Queue

# id of vk.com application, that has access to audio
APP_ID = '3358129'
# if None, then save mp3 in current folder
MUSIC_FOLDER = 'music'
# file, where auth data is saved
AUTH_FILE = '.auth_data'
# chars to exclude from filename
FORBIDDEN_CHARS = '/\\\?%*:|"<>!'


def get_saved_auth_params():
    access_token = None
    user_id = None
    try:
        with open(AUTH_FILE, 'rb') as pkl_file:
            token = pickle.load(pkl_file)
            expires = pickle.load(pkl_file)
            uid = pickle.load(pkl_file)
        if datetime.now() < expires:
            access_token = token
            user_id = uid
    except IOError:
        pass
    return access_token, user_id


def save_auth_params(access_token, expires_in, user_id):
    expires = datetime.now() + timedelta(seconds=int(expires_in))
    with open(AUTH_FILE, 'wb') as output:
        pickle.dump(access_token, output)
        pickle.dump(expires, output)
        pickle.dump(user_id, output)


def get_auth_params():
    auth_url = ("https://oauth.vk.com/authorize?client_id={app_id}"
        "&scope=audio&redirect_uri=http://oauth.vk.com/blank.html"
        "&display=page&response_type=token".format(app_id=APP_ID))
    webbrowser.open_new_tab(auth_url)
    redirected_url = raw_input("Paste here url you were redirected:\n")
    aup = urlparse.parse_qs(redirected_url)
    aup['access_token'] = aup.pop(
        'https://oauth.vk.com/blank.html#access_token')
    save_auth_params(aup['access_token'][0], aup['expires_in'][0],
        aup['user_id'][0])
    return aup['access_token'][0], aup['user_id'][0]


def get_tracks_metadata(access_token, user_id):
    url = ("https://api.vkontakte.ru/method/audio.get.json?"
        "uid={uid}&access_token={atoken}".format(
            uid=user_id, atoken=access_token))
    audio_get_page = urllib2.urlopen(url).read()
    return json.loads(audio_get_page)['response']


def get_track_full_name(t_data):
    html_parser = HTMLParser.HTMLParser()
    full_name = u"{0}_{1}".format(
        html_parser.unescape(t_data['artist'][:100]).strip(),
        html_parser.unescape(t_data['title'][:100]).strip(),
    )
    full_name = re.sub('[' + FORBIDDEN_CHARS + ']', "", full_name)
    full_name = re.sub(' +', ' ', full_name)
    return full_name + ".mp3"


def download_track(t_url, t_name):
    t_path = os.path.join(MUSIC_FOLDER or "", t_name)
    if not os.path.exists(t_path):
        print "Downloading {0}".format(t_name.encode('ascii', 'replace'))
        try:
            urllib.urlretrieve(t_url, t_path)
        except IOError as (errno, strerror):
            print "I/O error({0}): {1}".format(errno, strerror)


def main():
    access_token, user_id = get_saved_auth_params()
    if not access_token or not user_id:
        access_token, user_id = get_auth_params()
    tracks = get_tracks_metadata(access_token, user_id)
    if MUSIC_FOLDER and not os.path.exists(MUSIC_FOLDER):
        os.makedirs(MUSIC_FOLDER)
    return tracks

def worker(tracks, num):
    while not tracks.empty():
        t = tracks.get()
        t_name = get_track_full_name(t)
        download_track(t['url'], t_name)
        print "Done ", t_name, 'worker:', num
    print 'Tracks is empty worker:', num


if __name__ == '__main__':
    q = Queue()
    for i in main():
        q.put(i)
    gevent.monkey.patch_socket()
    gevent.monkey.patch_sys()
    gevent.joinall([gevent.spawn(worker, q, i) for i in xrange(10)])
    print 'All done'
