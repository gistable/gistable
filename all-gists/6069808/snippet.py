# -*- coding: utf8 -*-

# 下载速度很慢，
import urllib2, urllib
import sys
import os
import socket
import re

import socks
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9050, rdns=False)
socket.socket = socks.socksocket

# set urllib2 timeout
socket.setdefaulttimeout(300)

# config
INDEX_PAGE = 'http://learningenglish.voanews.com/programindex.html'
HOST = 'http://learningenglish.voanews.com'
VOA_DIR = os.path.join('D:\\', 'VOA')
RETRY_TIMES = 3

# re patterns
re_themes = re.compile('''<h4><a href=['"](.*?http.*?latest.*?)['"]>(.*?)</a></h4>''')
re_articles = re.compile('<h4.*?(/content/.*?/\d+\.html).*?</h4>')
re_article_title = re.compile('<title>\s+(.*)\s+</title>')
re_article_pdf = re.compile('''href=['"](.*pdf)['"]''')
re_audio_page = re.compile('/audio/Audio/\d+\.html')
re_article_audio = re.compile('(http:.*mp3)')

# helper
def download_data( url ):
    count = 0
    while count < RETRY_TIMES:
        count += 1
        data = urllib2.urlopen(url).read()
        if data:
            return data
        else:
            continue
    return ''

def save_url_to_file(url, file_path):
    # if file already exists and has the same length(in bytes) with the server, do not download data
    # if server do not return Content-Length header, then do not download again
    if os.path.isfile(file_path):
        # check length
        length_s = urllib.urlopen( url ).info().get('Content-Length', 0)
        length_l = os.path.getsize( file_path )
        #print 'length_s = ', repr(length_s)
        #print 'length_l = ', repr(length_l)
        if length_s == 0 or long(length_s) == (length_l):
            return True
    
    # so, redownload the file
    # when exception happen, delete the partly downloaded file
    try:
        urllib.urlretrieve(url, file_path, reporthook)
    except:
        os.remove( file_path)
        raise
    else:
        return True
    
# show download progress
def reporthook(blocks_read,block_size,total_size):  
    if not blocks_read:  
        print ("Connection opened")  
    if total_size <0:  
        #print "\rRead %d blocks"  % blocks_read
        sys.stdout.write("\rRead %d blocks   "  % blocks_read)
        sys.stdout.flush()
    else:  
        #print "\rdownloading: %d KB, totalsize: %d KB" % (blocks_read*block_size/1024.0,total_size/1024.0)
        sys.stdout.write("\rdownloading: %d KB, totalsize: %d KB   " % (blocks_read*block_size/1024.0,total_size/1024.0))
        sys.stdout.flush()
    	
# get themes
# theme name and page for latest articles
print 'From %s parsing themes ...' % INDEX_PAGE
html = download_data(INDEX_PAGE)
themes = re.findall(re_themes, html)
if themes:
    themes = set(themes)
    print 'Got %d themes:' % len(themes)
    for theme in themes:
        print 'Theme: %s. Page: %s.' % (theme[1], theme[0])
else:
    sys.exit()
  
for theme in themes:
    theme_name = theme[1]
    theme_index = theme[0]

    # get article's page
    theme_html = download_data(theme_index)
    if not theme_html: sys.exit()
    article_urls = re.findall(re_articles, theme_html)

    for article in article_urls:
        article_url = HOST + article
        print 'Getting info from %s' % article_url
        article_html = download_data(article_url)
        if not article_html: sys.exit()
        print 'Got it!'
        
        try:
            # get article title          
            article_title = re.search(re_article_title, article_html).groups()
            if not article_title: sys.exit()
            article_title =  '-'.join( re.findall('(\w+)', article_title[0]) )
            #article_title = '-'.join( article_title.split(' ') )
            print 'Got article title: %s' % article_title
          
            # get pdf url
            article_pdf = re.search(re_article_pdf, article_html).groups()
            if not article_pdf: sys.exit()
            article_pdf = article_pdf[0]
            print 'Got pdf url: %s' % article_pdf
            
            # get audio url
            audio_url = HOST + re.search(re_audio_page, article_html).group()
            print 'Getting info from audio_url %s' % audio_url
            audio_html = download_data(audio_url)
            if not audio_html: sys.exit()
            article_audio = re.search(re_article_audio, audio_html).group()
            print 'Got audio url: %s' % article_audio

            print 'Downloading PDF ...'
            file = os.path.join(VOA_DIR, article_title + '.pdf')
            if save_url_to_file( article_pdf, file):
                print 'OK'
            else:
                print 'Failed'
            print 'Downloading MP3 ...'
            #print str(article_audio)
            file = os.path.join(VOA_DIR, article_title + '.mp3')
            if save_url_to_file( article_audio, file):
                print 'OK'
            else:
                print 'Failed' 
            
        except AttributeError as e:
            pass
                       
print 'end'