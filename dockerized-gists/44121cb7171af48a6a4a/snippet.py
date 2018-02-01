#!/usr/bin/python
import os
import sys
import urllib2
import json
from BeautifulSoup import BeautifulSoup, NavigableString, Tag

USERNAME = ''
ICON_URL = ''
MATTERMOST_WEBHOOK_URL = '' # put your webhook url here
CHANNEL = ''


def get_picture_and_description():
    req = urllib2.Request('https://commons.wikimedia.org/wiki/Main_Page')
    page = urllib2.urlopen(req)
    soup = BeautifulSoup(page.read())
    picture_div = soup.find('div', {'id':'mf-picture-picture'})
    src_tag = picture_div.contents[1].find('img')
    desc_tag = picture_div.contents[1].find('span')
    src = src_tag['src']
    desc = ""
    for i in desc_tag.contents:
        if isinstance(i, NavigableString):
            desc+=i
        if isinstance(i, Tag):
            desc+=i.text
    return src, desc

def prepare_picture_of_a_day_markdown(src, desc):
    text = u"#### Picture of the day\n![]({1})\n {0}".format(desc, src)
    return text

def post_to_mattermost(text):
    data = {}
    data['text'] = text
    if len(USERNAME) > 0:
        data['username'] = USERNAME
    if len(ICON_URL) > 0:
        data['icon_url'] = ICON_URL
    if len(CHANNEL) > 0:
        data['channel'] = CHANNEL
    req = urllib2.Request(MATTERMOST_WEBHOOK_URL)
    req.add_header('Content-Type','application/json')
    payload = json.dumps(data)
    response = urllib2.urlopen(req, payload)
    if response.getcode() is not 200:
        print 'Posting to mattermost failed'

if __name__ == "__main__":
    MATTERMOST_WEBHOOK_URL = os.environ.get('MATTERMOST_WEBHOOK_URL', MATTERMOST_WEBHOOK_URL)
    CHANNEL = os.environ.get('CHANNEL', CHANNEL)
    USERNAME = os.environ.get('USERNAME', USERNAME)
    ICON_URL = os.environ.get('ICON_URL', ICON_URL)

    if len(MATTERMOST_WEBHOOK_URL) == 0:
        print 'MATTERMOST_WEBHOOK_URL must be configured.'
        sys.exit()

    src, desc = get_picture_and_description()
    text = prepare_picture_of_a_day_markdown(src, desc)
    post_to_mattermost(text)