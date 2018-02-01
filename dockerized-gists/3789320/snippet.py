#-*- coding: utf-8 -*-
import urllib, re, os, argparse

RE_NEXT_URL = ur'<a href=\"(?!javascript\:)([^\"]*?)">下一页<\/a>'
RE_PICTURE  = ur'<p\s+(?:align=\"center\")>\s*<img.*?src=\"(.*?)\".*?\/?>'
RE_ARCTITLE = ur'var arctitle=\'(.*?)\';'

def get_html(url):
    try:
        return urllib.urlopen(url).read().decode('gbk')
    except:
        return None

def get_next_url(url, html):
    m = re.search(RE_NEXT_URL, html, flags=re.I|re.M|re.S)
    href = m and m.group(1) or None
   
    if href:
        if href.startswith('/'):
            return re.sub(r'(http\:\/\/[^\/]+)(.*)', '\\1%s' % href, url)
        else:
            return re.sub(r'([^\/]*)$', href, url)
    else:
        return None

def get_pictures(html):
    return re.findall(RE_PICTURE, html, flags=re.I|re.M|re.S)

def get_title(html):
    m = re.search(RE_ARCTITLE, html, flags=re.I|re.M|re.S)
    return m and m.group(1) or None

def download_pictures(dirname, url, html):
    for picture in get_pictures(html):
        print 'Downloading', picture,
        filename = os.path.join(dirname, picture.split('/')[-1])
        try:
            resp = urllib.urlopen(picture)
            open(filename, 'wb+').write(resp.read())
            print ' [DONE]'
        except:
            print ' [FAIL]'
    
    next_url = get_next_url(url, html)
    print 'Fetching:', next_url
    html = next_url and get_html(next_url) or None
    html and download_pictures(dirname, next_url, html)
    
def execute(url):
    print 'Fetching %s' % url
    html = get_html(url)
    title = html and get_title(html) or None
    print 'Title:', title
    dirname = re.sub(r'\/', '', title)
    os.path.exists(dirname) or os.mkdir(dirname)
    title and download_pictures(dirname, url, html)
    os.system('nautilus "%s"' % dirname.encode('utf-8'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download 265g.com pictures.')
    parser.add_argument('url', help='Start url')
    args = parser.parse_args()
    execute(args.url)
