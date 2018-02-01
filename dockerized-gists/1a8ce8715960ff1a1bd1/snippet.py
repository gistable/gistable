#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import requests
from bs4 import BeautifulSoup
import codecs
import string
import random
import re
import getpass


user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/36.0.1985.143 Safari/537.36")


def randomString(length):
    return ''.join(random.choice(string.letters + string.digits) for i in xrange(length))


def signin(email, password):
    signin_url = "https://accounts.coursera.org/api/v1/login"
    logininfo = {"email": email,
                 "password": password,
                 "webrequest": "true"
                 }

    XCSRF2Cookie = 'csrf2_token_%s' % ''.join(randomString(8))
    XCSRF2Token = ''.join(randomString(24))
    XCSRFToken = ''.join(randomString(24))
    cookie = "csrftoken=%s; %s=%s" % (XCSRFToken, XCSRF2Cookie, XCSRF2Token)

    post_headers = {"User-Agent": user_agent,
                    "Referer": "https://accounts.coursera.org/signin",
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRF2-Cookie": XCSRF2Cookie,
                    "X-CSRF2-Token": XCSRF2Token,
                    "X-CSRFToken": XCSRFToken,
                    "Cookie": cookie
                    }
    try:
        login_res = coursera_session.post(signin_url,
                                          data=logininfo,
                                          headers=post_headers,
                                          )
    except requests.exceptions.RequestException, e:
        print "Post failed...\n", e
        sys.exit(2)

    if login_res.status_code == 200:
        print "Login Successfully!"
    else:
        print "Login failed..."
        sys.exit(2)


def get_content(url):
    try:
        url_response = coursera_session.get(url, timeout=2)
        url_response.raise_for_status()
        return url_response.text
    except requests.exceptions.RequestException, e:
        print "Bad request...\n", e
        sys.exit(2)


def get_resource(content, chapters, lecture_resource):
    soup = BeautifulSoup(content)

    chapter_list = soup.find_all("div", class_="course-item-list-header")
    lecture_resource_list = soup.find_all("ul", class_="course-item-list-section-list")

    ppt_pattern = re.compile(r'https://[^"]*\.ppt[x]?')
    pdf_pattern = re.compile(r'https://[^"]*\.pdf')
    for lecture_item, chapter_item in zip(lecture_resource_list, chapter_list):
        chapter = chapter_item.h3.text.lstrip()
        chapters[chapter] = []
        for lecture in lecture_item:
            lecture_name = lecture.a.string.lstrip()
            chapters[chapter].append(lecture_name)
            lecture_resource[lecture_name] = []

            # get resource link
            ppt_tag = lecture.find(href=ppt_pattern)
            pdf_tag = lecture.find(href=pdf_pattern)
            srt_tag = lecture.find(title="Subtitles (srt)")
            mp4_tag = lecture.find(title="Video (MP4)")

            for resource in (ppt_tag, pdf_tag, srt_tag, mp4_tag):
                if resource:
                    lecture_resource[lecture_name].append(resource["href"])
                else:
                    lecture_resource[lecture_name].append(None)


def generate_feed(chapters, lecture_resource):
    with codecs.open("feed.sh", "w", "utf-8") as f:
        for chap in chapters:
            f.write("mkdir '{0}'\n".format(chap))
            f.write("cd '{0}'\n".format(chap))

            for lecture in chapters[chap]:
                ppt = lecture_resource[lecture][0]
                pdf = lecture_resource[lecture][1]
                srt = lecture_resource[lecture][2]
                mp4 = lecture_resource[lecture][3]
                if ppt:
                    f.write("curl {0} -o '{1}.pptx'\n".format(ppt, lecture))
                if pdf:
                    f.write("curl {0} -o '{1}.pdf'\n".format(pdf, lecture))
                if srt:
                    f.write("curl {0} -o '{1}.srt'\n".format(srt, lecture))
                if mp4:
                    f.write("curl {0} -o '{1}.mp4'\n".format(mp4, lecture))
            f.write("cd ..\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Invalid input.\nUseage: python ", sys.argv[0], " [couresname]"
        sys.exit(2)
    coursera_session = requests.Session()
    email = raw_input("Email: ")
    password = getpass.getpass()
    signin(email, password)

    lesson_url = "https://class.coursera.org/" + sys.argv[1] + "/lecture"
    chapters = {}
    lecture_resource = {}
    lesson_content = get_content(lesson_url)
    print "Get url successfully!"
    get_resource(lesson_content, chapters, lecture_resource)
    print "Get resource successfully!"
    generate_feed(chapters, lecture_resource)
    print "Generate feed successfully!"