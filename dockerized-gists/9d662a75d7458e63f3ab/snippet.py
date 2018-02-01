#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import logging
import datetime
import requests
import BeautifulSoup
from requests.adapters import HTTPAdapter


logger = logging.getLogger("v2ex")
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
file_handler = logging.FileHandler("/var/log/v2ex.log")
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler(sys.stderr)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


class V2EX:
    """
    v2ex auto login and execute daily task get gold coins 
    """

    def __init__(self, username, password):
        self.signin_url = "http://www.v2ex.com/signin"
        self.daily_url = "http://www.v2ex.com/mission/daily"
        self.v2ex_url = "http://www.v2ex.com"
        self.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.94 Safari/537.36"

        self.headers = {
            "User-Agent": self.user_agent,
            "Referer": self.v2ex_url,
        }
        v2ex_session = {}
        soup = {}
        self.username = username
        self.password = password
        self.v2ex_session = requests.Session()
        self.v2ex_session.mount(self.v2ex_url, HTTPAdapter(max_retries=5))
        self.soup = BeautifulSoup.BeautifulSoup()
        logger.debug("v2ex init")

    def login(self):
        # get login_info random 'once' value
        v2ex_main_req = self.v2ex_session.get(
            self.signin_url,
            headers=self.headers
        )
        v2ex_main_tag = BeautifulSoup.BeautifulSoup(v2ex_main_req.content)
        form_tag = v2ex_main_tag.find(
            'form', attrs={"method": "post", "action": "/signin"}
        )
        input_once_tag = form_tag.find('input', attrs={"name": "once"})
        input_once_value = input_once_tag.attrs[1][1]
        login_info = {
            "next": "/",
            "u": self.username,
            "p": self.password,
            "once": input_once_value,
            "next": "/"
        }

        print login_info
        self.headers["Referer"] = self.signin_url
        # login
        self.v2ex_session.post(
            self.signin_url, 
            data=login_info, 
            headers=self.headers
        )

        
        main_req = self.v2ex_session.get(self.v2ex_url, headers=self.headers)
        self.soup = BeautifulSoup.BeautifulSoup(main_req.content)
        top_tag = self.soup.find('div', attrs={"id": "Top"})
        user_tag = top_tag.find(href="/member/" + self.username)
        if not user_tag:
            logger.debug("v2ex signin failed for %s", self.username)
            return False
        else:
            logger.debug("v2ex signin successed for %s", self.username)
            return True

    def unchecked(self):
        award_tag = self.soup.find(href="/mission/daily")
        if award_tag:
            return True
        else:
            logger.debug("v2ex has already checked in")
            return False

    def checkin(self):
        # get award if haven't got it
        get_award_req = self.v2ex_session.get(
            self.daily_url, 
            headers=self.headers
        )
        get_award_soup = BeautifulSoup.BeautifulSoup(get_award_req.content)
        button_tag = get_award_soup.find('input', attrs={'type': 'button'})
        click_href = button_tag.attrs[3][1]
        first_dot_index = click_href.find("'")
        last_dot_index = click_href.find("'", first_dot_index + 1)
        click_url = self.v2ex_url + click_href[first_dot_index + 1: last_dot_index]

        self.headers["Referer"] = self.daily_url
        award_req = self.v2ex_session.get(click_url, headers=self.headers)

        if award_req.status_code == requests.codes.ok:
            logger.debug("v2ex checkin successfully ! ")
        else:
            logger.debug("v2ex checkin failed with %s", self.username, " ! \n")

    def run(self):
        if self.login():
            if self.unchecked():
                self.checkin()


if __name__ == '__main__':
    username = ''
    password = ''
    v2ex = V2EX(username, password)
    v2ex.run()