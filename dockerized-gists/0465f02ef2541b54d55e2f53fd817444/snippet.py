#!/usr/bin/python

import sys
import os
import argparse
import re
import youtube_dl
import requests

from splinter import Browser
from bs4 import BeautifulSoup
from clint.textui import progress


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", dest="user", required=True,
                        help="user email")
    parser.add_argument("-p", "--password", dest="password", required=True,
                        help="user password")
    parser.add_argument("-c", "--course", dest="course", required=True,
                        help="course link")
    args = parser.parse_args()

    login(args.user, args.password)  # login with splinter
    course_links = course_index(args.course)  # extract TOC links

    directories = ["{}. {}".format(number, name[0])
                   for number, name
                   in enumerate(course_links)]  # dir list
    makedir(directories)

    for number, dir in enumerate(directories):  # traverse directories
        os.chdir(dir)
        download_video(course_links[number][1])  # download video using yt
        # course_files(course_links[number][1]) # download files
        os.chdir('..')


def course_name(link):
    name = link.findAll('span', {"class": ['lecture-name']})
    if len(name) >= 1:
        return (name[0]
                .text.strip().rstrip()
                .replace("  ", '')
                .replace('\n', '')
                .replace('(', ' ('))


def course_index(course):
    browser.visit(course)
    soup = BeautifulSoup(browser.html, "html5lib")
    links = soup.findAll('a',
                         attrs={'href': re.compile("\/.+[0-9]\/lectures\/.+[0-9]")})
    course_links = [(course_name(link), base + link['href'])
                    for link in links[1:]]
    return course_links


def makedir(directories):
    for dir in directories:
        if not os.path.exists(dir):
            os.mkdir(dir)


def login(user, password):
    url = "https://sso.teachable.com/secure/61349/users/sign_in?clean_login=true&reset_purchase_session=1"
    browser.visit(url)
    browser.fill('user[email]', user)
    browser.fill('user[password]', password)
    button = browser.find_by_name('commit')
    button.click()


def download_file(url, name):
    r = requests.get(url, stream=True)
    path = name
    with open(path, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024),
                                  expected_size=(total_length / 1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()


def course_files(url):
    browser.visit(url)
    soup = BeautifulSoup(browser.html, "html5lib")
    files = [(i.text.rstrip().strip(), i['href'])
             for i in soup.findAll('a', {'class': 'download'})]
    download_file(files[0][1], files[0][0])


def download_video(url):
    ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
    with ydl:
        result = ydl.extract_info(
            url,
            download=False  # We just want to extract the info
        )
    video = result
    print(video, video['url'])


if __name__ == "__main__":
    browser = Browser('phantomjs')
    base = "https://veduca.org"
    main()
