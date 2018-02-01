#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
まとめサイトなどURLに含まれるYouTubeをプレイリストに保存する

    $ python youtube_gdata_playlist.py http://...

'''
# 以下要設定
# cf. YouTubeクライアント
# https://developers.google.com/youtube/1.0/developers_guide_python#ClientLogin
####

username = ''
email = ''
password = ''
developer_key = ''

####

import sys
import time
import re
import urllib2
import gdata.youtube
import gdata.youtube.service
from BeautifulSoup import BeautifulSoup

class YouTube(object):
    """
    YouTube Data API
    https://code.google.com/p/gdata-python-client/
    https://developers.google.com/youtube/1.0/developers_guide_python
    """
    def __init__(self, username, email, password, developer_key):
        
        self.yt_service = gdata.youtube.service.YouTubeService()
        self.yt_service.ssl = True
        self.username = username

        # ClientLogin for installed applications
        self.yt_service.email = email
        self.yt_service.password = password
        self.yt_service.developer_key = developer_key
        self.yt_service.ProgrammaticLogin()
        
    def AddPlaylist(self, title, description=""):
        '''
        プレイリストを追加する
        https://developers.google.com/youtube/1.0/developers_guide_python#AddingPlaylists

        Parameters
        ==========
        - title : str
        - description : str

        Returns
        =======
        playlist_uri : str
        '''
        # タイトルと説明を表示
        limit = 0
        for i in range(len(title)):
            if limit > 60:
                break
            if ord(title[i]) > 255:
                limit += 3
            else:
                limit += 1
        tmp_title = title[:i] if i != len(title) - 1 else title

        print title # 20字
        print description
        new_public_playlistentry = self.yt_service.AddPlaylist(tmp_title, description)

        if isinstance(new_public_playlistentry, gdata.youtube.YouTubePlaylistEntry):
            print 'New playlist added'
            return 'http://gdata.youtube.com/feeds/playlists/' + new_public_playlistentry.id.text.split('/')[-1]
        else:
            return None

    def AddVideoToPlaylist(self, playlist_uri, video_id):
        '''
        プレイリストにビデオを追加する

        Parameters
        ==========
        - playlist_uri : str
        - video_id : str
        '''
        playlist_video_entry = self.yt_service.AddPlaylistVideoEntryToPlaylist(
            playlist_uri, video_id)

        if isinstance(playlist_video_entry, gdata.youtube.YouTubePlaylistVideoEntry):
            print video_id

def get_video_ids(url):
    '''
    urlに含まれるYouTubeのvideo idを抽出する
    '''
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    title = soup('title')[0].string
    video_ids = []
    targets = [['embed', 'src', 'v\/([-\w]+)'],
               ['iframe', 'src', 'youtube.com\/embed\/([-\w]+)'],
               ['a', 'href', 'youtube.com\/watch\?v=([-\w]+)'],
               ['a', 'href', 'youtu\.be\/([-\w]+)']]
    for tag, attr, exp in targets:
        for element in soup(tag):
            src = element.get(attr)
            if src:
                result = re.search(exp, src)
                if result:
                    video_ids.append(result.group(1))
    tmp = []
    for video_id in video_ids:
        if video_id not in tmp:
            tmp.append(video_id)
    return title, tmp

if __name__ == '__main__':
    try:
        # コマンドライン引数から取得先のURL
        url = sys.argv[1]
    except:
        exit()

    # urlのタイトルと含まれるビデオの取得
    title, video_ids = get_video_ids(url)
    print len(video_ids)

    # YouTubeクラスインスタンス
    yt = YouTube(username, email, password, developer_key)

    # プレイリストの作成
    playlist_uri = yt.AddPlaylist(title, title + " - " + url)

    # 失敗
    failed = []
    # リトライ回数
    retry = 0
    # ビデオ番号
    n = 0

    # ビデオがあってリトライ回数が10を超えない限り継続
    while video_ids and retry < 10:
        n += 1
        print n,
        video_id = video_ids.pop(0)
        try:
            yt.AddVideoToPlaylist(playlist_uri, video_id)
            time.sleep(1)
        except gdata.service.RequestError as e:
            print video_id
            print type(e), e
            # 短期間にアクセスしすぎないように．．．
            if 'too_many_recent_calls' in str(e):
                video_ids = [video_id] + video_ids
                time.sleep(40) # 40秒待機
                retry += 1
                n -= 1
        except:
            failed.append(video_id)
            print video_id
            print sys.exc_info()

    # 残り
    print 'rest: %s' % ','.join(video_ids)
    # エラー
    print 'failed: %s' % ','.join(failed)
    # プレイリストURI
    print playlist_uri
