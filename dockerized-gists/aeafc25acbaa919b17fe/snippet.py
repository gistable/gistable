from bs4 import BeautifulSoup
from lxml import html
from urllib2 import urlopen, Request, HTTPError, URLError
import urllib2
import urllib
import urlparse
import json
import os

__author__ = 'arul'

"""
    This Program can download only the tutorials which are freely available in https://tutsplus.com
"""

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
global headers
headers = {
    "User-Agent": USER_AGENT,
    "Referer": "https://tutsplus.com"
}

TUTSPLUS_USER_NAME = "your@emailaddress"
TUTSPLUS_USER_PASSWORD = "yourtutspluspassword"

DOWNLOAD_FOLDER = "videos"
COURSE_URL = "https://code.tutsplus.com/courses/30-days-to-learn-jquery"


def do_login():
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(opener)
    sign_url = "https://tutsplus.com/sign_in"
    sign_content = get_content(sign_url)
    if sign_content:
        tree = html.document_fromstring(sign_content)
        authenticity_token = tree.xpath("//*[@name='authenticity_token']/@value")

    print "authenticity_token : %s" % list(set(authenticity_token))

    login_url = "https://tutsplus.com/sessions"
    authparams = dict()
    authparams["authenticity_token"] = authenticity_token[0]
    authparams["session[login]"] = TUTSPLUS_USER_NAME
    authparams["session[password]"] = TUTSPLUS_USER_PASSWORD
    params = urllib.urlencode(authparams)
    f = urlopen(Request(login_url, None, headers), params)
    print f.info()
    f.close()

def get_content(__url__):
    __content__ = None
    try:
        response = urlopen(Request(__url__, None, headers))
        __content__ = response.read()
    except HTTPError as e:
        print "Failed.. %r" % e.code
        print e.read()
    except URLError as e:
        if hasattr(e, 'reason'):
            print "Failed to reach the server..."
        else:
            # Everything else
            raise
    if __content__:
        soup = BeautifulSoup(__content__)
        return soup.prettify()
    else:
        return None

def download_binary(_file_name_, _url_):
    print "Downloading %s " % _file_name_
    req = urllib2.urlopen(_url_)
    CHUNK = 16 * 1024
    with open(_file_name_, 'wb') as fp:
        while True:
            chunk = req.read(CHUNK)
            if not chunk:
                break
            fp.write(chunk)


if __name__ == "__main__":
    #Programs starts here
    do_login()
    course_content = get_content(COURSE_URL)
    if course_content:
        tree = html.document_fromstring(course_content)
        links = tree.xpath("//a[@class='lesson-index__lesson-link']/@href")
        print links
        print "No of Lessons : %d" % len(links)

        video_urls = list()
        base_url = urlparse.urlparse(COURSE_URL).netloc
        for link in links:
            lesson_url = "https://%s/%s" % (base_url, link)
            lesson_content = get_content(lesson_url)
            tree = html.document_fromstring(lesson_content)
            wistia_id = tree.xpath("//*[contains(@class,'lesson-video--full-size')]/@data-wistia-id")

            if wistia_id and len(wistia_id) == 1:
                wistia_id = wistia_id[0]

            wistia_name = tree.xpath("//*[contains(@class,'lesson-video--full-size')]/@data-human-readable-id")
            if wistia_name and len(wistia_name) == 1:
                wistia_name = wistia_name[0]

            wistia_json_url = "https://fast.wistia.com/embed/medias/%s.json" % wistia_id
            request = Request(wistia_json_url, None, headers)
            wistia_json = urlopen(request).read()
            print wistia_json
            parsed = json.loads(wistia_json)
            if "media" in parsed:
                media = parsed["media"]
                if "assets" in media:
                    assets = media["assets"]
                    if "original" in assets:
                        original = assets["original"]
                        video_url = original["url"]
                        ext = original["ext"]
                        video_urls.append((wistia_name+"."+ext, video_url))

        # Create Download dir if not exists
        if not os.path.exists(DOWNLOAD_FOLDER):
            os.makedirs(DOWNLOAD_FOLDER)

        # Downloading all lessons
        for video_info in video_urls:
            print video_info
            download_name, download_url = video_info
            download_binary(DOWNLOAD_FOLDER +'/'+ download_name, download_url)