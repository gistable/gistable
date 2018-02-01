# coding=utf-8 
from BeautifulSoup import BeautifulSoup
import urllib2
import sys, os

reload(sys) 
sys.setdefaultencoding('utf-8')

input_file = sys.argv[1]
output_opml = sys.argv[2]
error_url = sys.argv[3]
proxy = "127.0.0.1:8087"
proxies = {"http":"http://%s" % proxy}

input_data = open(input_file,"r").readlines()
output = file(output_opml,"w")
error = file(error_url,"w")
opml_start = """<?xml version="1.0" encoding="UTF-8"?>
<opml version="1.0">
    <head>
        <title>lwjef subscriptions in Google Reader</title>
    </head>
    <body>
"""
opml_end = """    </body>
</opml>"""
opml_outline_format = """        <outline text="%(title)s" title="%(title)s" type="rss"
            xmlUrl="%(rss_url)s" htmlUrl="%(input_url)s"/>
"""


def main():
    output.write(opml_start)
    for line in input_data:
        input_url = line.join(line.split())

        if input_url[:7]!="http://":
            input_url = "http://" + input_url
        
        headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language':'en-us,en;q=0.5',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Keep-Alive':'300',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0'
        }

        proxy_support = urllib2.ProxyHandler(proxies)
        opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler(debuglevel=1))
        urllib2.install_opener(opener)

        req = urllib2.Request(input_url, None, headers)
        try:
            doc = urllib2.urlopen(req).read()
        except urllib2.HTTPError:
            error.write(input_url)
            error.write("\n")
            continue
        except urllib2.URLError:
            error.write(input_url)
            error.write("\n")
            continue
            
        
        soup = BeautifulSoup(doc)
        alt = soup.find('link', rel="alternate", type="application/rss+xml")
        try:
            title = soup.html.title.renderContents()
        except AttributeError:
            error.write(input_url)
            error.write("\n")
            continue
        if alt is None:
            alt = soup.find('link', rel="alternate", type="application/atom+xml")
        if alt is not None:
            rss_url = alt['href']
        if rss_url[:7] == "http://":
            opml_outline = opml_outline_format % {'title':title, 'input_url':input_url, 'rss_url':rss_url}
            output.write(opml_outline)
    output.write(opml_end)
    output.close()


if __name__ == "__main__":
    main()
