# A script that can automatically download videos from Edx
# Currently this is heavily tied to the way my Edx account and my computer is
# set up. It downloads by sending the the download url and download directory 
# to aria2 runnig in rpc mode. 
# More info here: http://aria2.sourceforge.net/manual/en/html/aria2c.html#rpc-interface
# You can use http://ziahamza.github.io/webui-aria2/ to see download progress
# For now parameters, such as username, password, and which course to download 
# can be provided in the script
# I intend to make it more flexible
from __future__ import print_function

import xmlrpclib

import requests
from bs4 import BeautifulSoup


class Edx(object):
    BASE_URL = 'https://courses.edx.org'
    LOGIN_URL = BASE_URL + '/login_ajax'
    DASHBOARD_URL = BASE_URL + '/dashboard'

    def __init__(self, email, password):
        self.__session = requests.Session()
        s = self.__session
        token = s.get(self.LOGIN_URL).cookies['csrftoken']
        r = s.post(self.LOGIN_URL, data={
            'email': email,
            'password': password,
            'remember': False,
        }, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:24'
                          '.0) Gecko/20100101 Firefox/24.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            'Referer': self.LOGIN_URL,
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': token,
        })

        self.soup = BeautifulSoup(s.get(self.DASHBOARD_URL).text)
        self.courses = {}
        try:
            self.courses = pickle.load(open('data.p', 'rb'))
        except IOError as e:
            print("Cached data not available, downloading from scratch")

    def get_courses(self):
        if self.courses == {}:
            print("Loading Course Data")
            for course in self.soup.find_all('li', class_='course-item'):
                title = course.find('h3').text.strip()
                url = self.BASE_URL + course.article.a['href'].strip()
                self.courses[title] = {'url': url}
            for course in self.courses:
                print("Loading info for Course: %s" % course)
                self.get_course_info(course)
        pickle.dump(self.courses, open('data.p', 'wb'))
        return self.courses

    def get_course_info(self, course):
        course_data = self.courses.get(course)
        if 'chapters' in course_data:
            return course_data['chapters']
        s = self.__session
        r = s.get(course_data['url'].replace('info', 'courseware'))
        soup = BeautifulSoup(r.text)
        chapters = {}
        for chapter in soup.find_all('div', class_='chapter'):
            title = chapter.h3.a.text.strip()
            url = self.BASE_URL + chapter.ul.li.a['href']
            chapters[title] = {'url': url, 'sections': {}}
            for section in chapter.find_all('li'):
                section_title = section.a.p.text.strip()
                section_url = self.BASE_URL + section.a['href']
                chapters[title]['sections'][section_title] = {
                    'url': section_url}
        course_data['chapters'] = chapters
        for chapter in chapters:
            self.get_chapter_info(course, chapter)
        return chapters

    def get_chapter_info(self, course, chapter):
        course_data = self.courses.get(course)
        chapter_data = course_data['chapters'][chapter]
        for section in chapter_data['sections']:
            self.get_section_info(course, chapter, section)
        return chapter_data
        #chapter_url = chapter.get('url')

    def get_section_info(self, course, chapter, section):
        course_data = self.courses.get(course)
        chapter_data = course_data['chapters'][chapter]
        section_data = chapter_data['sections'][section]
        s = self.__session
        r = s.get(section_data['url'])
        soup = BeautifulSoup(r.text)
        videos = []
        for content in soup.find_all('div', class_='seq_contents'):
            resoup = BeautifulSoup(content.text)
            for video in resoup.find_all('li', class_='video-sources'):
                videos.append(video.a['href'])

        section_data['videos'] = videos
        return section_data

    def download_all_from_section(self, course, chapter, section):
        course_data = self.courses.get(course)
        chapter_data = course_data['chapters'][chapter]
        section_data = chapter_data['sections'][section]
        for i, video in enumerate(section_data['videos']):
            s = xmlrpclib.ServerProxy("http://localhost:6800/rpc")
            s.aria2.addUri([video], {'dir': '~/Studies/EdX/'
                                            + course + '/'
                                            + chapter + '/'
                                            + section + '/'
                                            + str(i) + '/'})

    def download_all_from_chapter(self, course, chapter):
        course_data = self.courses.get(course)
        chapter_data = course_data['chapters'][chapter]
        for section in chapter_data['sections']:
            self.download_all_from_section(course, chapter, section)

    def download_all_from_course(self, course):
        course_data = self.courses.get(course)
        for chapter in course_data['chapters']:
            self.download_all_from_chapter(course, chapter)

    def download_all(self):
        for course in self.courses:
            self.download_all_from_course(course)


import cPickle as pickle

e = Edx('email', 'password')
e.get_courses()

# Full course name, e.g. Louv1.01x Paradigms of Computer Programming
e.download_all_from_course('full course name') 