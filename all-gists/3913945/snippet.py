#!/usr/bin/python3

feedURLs = ['http://www.jw.org/apps/U_sFFZRQVNZNT?rln=U&rmn=g&rfm=m4b',
            'http://www.jw.org/apps/U_sFFZRQVNZNT?rln=U&rmn=w&rfm=m4b',
            'http://www.jw.org/apps/U_sFFZRQVNZNT?rln=U&rmn=wp&rfm=m4b',
            'http://www.jw.org/apps/U_sFFCsVrGZNT?rln=U&rmn=g&rfm=pdf',
            'http://www.jw.org/apps/U_sFFCsVrGZNT?rln=U&rmn=w&rfm=pdf',
            'http://www.jw.org/apps/U_sFFCsVrGZNT?rln=U&rmn=wp&rfm=pdf',
            'http://www.jw.org/apps/E_sFFCsVrGZNT?rln=E&rmn=g&rfm=pdf',
            'http://www.jw.org/apps/E_sFFCsVrGZNT?rln=E&rmn=w&rfm=pdf',
            'http://www.jw.org/apps/E_sFFCsVrGZNT?rln=E&rmn=wp&rfm=pdf',
            'http://www.jw.org/apps/E_sFFCsVrGZNT?rln=E&rmn=ws&rfm=pdf']

# directories where to store pdf and mp3 files.
dirs = { 'pdf': '/media/media/files/magazines/', 
         'zip': '/media/media/audio/Podcasts/' }

import os
import sys
import re
import feedparser
import json
import urllib

def mkdir_recursive(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == os.errno.EEXIST:
            pass
        else: raise
        
def downloadFile(url, filename):
    import urllib
    showStatus('Init')
    sys.stdout.write(' ' + url + ' ')
    urllib.request.urlretrieve(url, filename, reporthook=downloadProgress)

def showStatus(text):
    sys.stdout.write('\r -- [%6s]' % text.center(6))
    sys.stdout.flush()

def downloadProgress(count, blockSize, totalSize):
    percent = int(count*blockSize*100/totalSize)
    if percent >= 100:
        showStatus('Done')
        return
    showStatus('%3d%%' % percent)

def unpackFile(fileName, dirName):
    import zipfile
    showStatus('UnPack')
    zipfile.ZipFile(fileName).extractall(dirName)
    os.remove(fileName)
    showStatus('Done')

def main():
    for url in feedURLs:
        sys.stdout.write('.')
        sys.stdout.flush()
        feed = feedparser.parse(url)
        for item in feed.entries:
            # uncomment this block to exclude large print
            # if item.link.find('f-lp') != -1:
            #     continue
            meta = re.search('/(?P<filename>(?P<code>[^_/]+(_f-lp-[12])?)_(?P<lang>[A-Z])_(?P<issue>(?P<year>\d{4})(?P<month>\d\d)).*\.(?P<ext>.*))$', item.link).groupdict()
            if meta['ext'] == 'm4b':
                if len(meta['issue']) == 6:
                    meta['issue'] += '01'
                dirName = os.path.join(dirs['zip'], meta['year'], meta['month'], meta['code'])
                fileName = os.path.join(dirName, meta['filename'].replace('.m4b', '.zip'))
                if os.path.isdir(dirName):
                    continue
                mkdir_recursive(dirName)
                jsonurl = 'http://www.jw.org/apps?index.html?fileformat=MP3&issue=%s&output=json&pub=%s&langwritten=%s&option=TRGCHlZRQVNYVrXF'
                request = urllib.request.urlopen(jsonurl % (meta['issue'], meta['code'], meta['lang']))
                info = json.loads(request.read().decode(encoding='UTF-8'))
                downloadFile(info['files']['U']['MP3'][0]['file']['url'], fileName)
                unpackFile(fileName, dirName)
            else:
                dirName = os.path.join(dirs['pdf'], meta['lang'], meta['year'])
                fileName = os.path.join(dirName, meta['filename'])
                if os.path.isfile(fileName):
                    continue
                mkdir_recursive(dirName)
                downloadFile(item.link, fileName)
            sys.stdout.write('\n')

    sys.stdout.write(' Done.\n')
    
if __name__ == '__main__':
    main()
