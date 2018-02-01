from sys import argv
import os
import re
import subprocess
import urllib.request
import urllib.parse
import youtube_dl
from gi.repository import Notify


def url_basename(url):
    path = urllib.parse.urlparse(url).path
    return path.strip('/').split('/')[-1]

def absolute_url(url, base_url):
    return url if re.match(r'^https?://', url) else urllib.parse.urljoin(base_url, url)

with youtube_dl.YoutubeDL({}) as ydl:
    info = ydl.extract_info(argv[1], download=False)
    if info['protocol'].startswith('m3u8'):
        url = info['url']
        title = info['title']
        http_headers = info['http_headers']
        if not os.path.exists('%s/media_segments' % title):
            request = urllib.request.Request(url, headers=http_headers)
            media_playlist = urllib.request.urlopen(request).read().decode()
            if not os.path.exists(title):
                os.makedirs(title)
            with open('%s.m3u8' % title, 'w') as mod_media_playlist:
                with open('%s/media_segments' % title, 'w') as media_segments:
                    for line in media_playlist.splitlines():
                        line = line.strip()
                        if line:
                            if not line.startswith('#'):
                                segment_url = absolute_url(line, url)
                                media_segments.write(segment_url + '\n')
                                line = '%s/%s' % (title, url_basename(segment_url))
                            elif line.startswith('#EXT-X-KEY:'):
                                key_url = absolute_url(re.search('URI="([^"]+)"', line).group(1), url)
                                key_path = '%s/%s' % (title, url_basename(key_url))
                                request = urllib.request.Request(key_url, headers=http_headers)
                                with open(key_path, 'wb') as key:
                                    key.write(urllib.request.urlopen(request).read())
                                line = line.replace('URI="%s"' % key_url, 'URI="%s"' % key_path)
                            mod_media_playlist.write(line + '\n')
        os.chdir(title)
        cmd = ['aria2c', '-j', '1', '--on-download-complete', '', '--on-download-error', '', '--save-session', 'media_segments', '-i', 'media_segments']
        for key, val in http_headers.items():
            cmd += ['--header', '%s: %s' % (key, val)]
        try:
            Notify.init("M3U8 Downloader")
            p = subprocess.Popen(cmd)
            p.communicate()
            Notification = Notify.Notification.new('M3U8 Downloader', 'download completed', 'dialog-information')
        except:
            Notification = Notify.Notification.new('M3U8 Downloader', 'download failed', 'dialog-information')
        Notification.show()
    else:
        ydl.process_ie_result(info)