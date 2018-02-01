# EDIT: 2013/10/20
# google has updated its kwt UI, this script doesn't work any more!
# may be I will update this script when I have time to investigate their new Interface.

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import selenium.webdriver.support.wait
selenium.webdriver.support.wait.POLL_FREQUENCY = 0.05

import re
import random
import collections

class AdwordsAutomater(object):
    def __init__(self, email, passwd):
        self.email = email
        self.passwd = passwd
        try:
            self.ff = webdriver.Chrome()
        except:
            self.ff = webdriver.Firefox()
            self.ff.set_page_load_timeout(30)
        self.ff.implicitly_wait(30)
        self.busy = False
        self.is_login = False
        self.on_keyword_page = False
        self.kwurl = ''

    def login(self):
        email, passwd = self.email, self.passwd
        try:
            print 'getting adwords.google.com'
            self.ff.get('https://adwords.google.com')
        except TimeoutException:
            pass
        self.ff.find_element_by_id("Email").send_keys(email)
        self.ff.find_element_by_id("Passwd").send_keys(passwd)
        signin = self.ff.find_element_by_id('signIn')
        try:
            print 'submit login form'
            signin.submit()
        except TimeoutException:
            pass
        self.is_login = True
        search = re.compile(r'(\?[^#]*)#').search(self.ff.current_url).group(1)
        self.kwurl = 'https://adwords.google.com/o/Targeting/Explorer'+search+'&__o=cues&ideaRequestType=KEYWORD_IDEAS';

    def find_keyword_volumes(self, keywords):
        if not self.is_login:
            self.login()

        if not isinstance(keywords, collections.Iterable):
            keywords = [ keywords ]

        print self.email, 'querying', keywords
        self.busy = True
        ret = {}

        print 'visiting keyword tools'
        self.ff.get(self.kwurl)

        kwinput = self.ff.find_element_by_class_name("sEAB")
        kwinput.send_keys('\n'.join(keywords))

        self.ff.find_element_by_css_selector("button.gwt-Button").click()

        try:
            # wait for at least one elements ready, implicitly
            self.ff.find_elements_by_xpath('//tr//*[contains(text(),"{0}")]'.format(random.choice(keywords)))
        except TimeoutException:
            # if we fail, fail gracefully
            pass
        else:
            text = self.ff.find_elements_by_xpath('//table[@class="sMNB"]')[0].text
            texts = text.split('\n')
            for i in range(1,len(texts)/4):
                ret[ texts[i*4] ] = (texts[i*4+2], texts[i*4+3])

        self.busy = False

        return ret

if __name__ == "__main__":
    aa = AdwordsAutomater(email="REPLACE_THIS_ADDRESS", passwd="REPLACE_THIS_PASSWORD")
    print aa.find_keyword_volumes(["ipad","cars","a0012k2k2","kindle","mac","beats","travel"])
