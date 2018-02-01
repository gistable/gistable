#!/usr/bin/env python

import re, urlparse

from selenium import webdriver
from time import sleep
import unittest
#Articles
#http://toddhayton.com/2015/02/03/scraping-with-python-selenium-and-phantomjs/
#https://realpython.com/blog/python/headless-selenium-testing-with-python-and-phantomjs/

#Docs
#http://seleniumhq.github.io/selenium/docs/api/py/webdriver_remote/selenium.webdriver.remote.webelement.html#module-selenium.webdriver.remote.webelement
#https://docs.python.org/2/library/re.html?highlight=reg%20exp#re.MatchObject.groupdict

r = re.compile(r'jobdetail\.ftl\?job=(?P<job_id>\d+)')

class Test(unittest.TestCase):
    def testRegex(self):
        
        urls = ['/careersection/l3_ext_us/jobdetail.ftl?job=071197', '/careersection/l3_ext_us/071197']
        results = []
        for url in urls:
            m = r.search(url)
            if (m != None):
                gd = m.groupdict()
                results.append(gd['job_id'])
            else:
                results.append('')
        self.assertEqual(results[0], '071197')
        self.assertEqual(results[1], '')


class Scraper(object):
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.jobs = []
        self.link = 'https://l3com.taleo.net/careersection/l3_ext_us/jobsearch.ftl'
        self.maxpage = 5
        self.delay = 2

    def addJob(self, info):
        m = r.search(info['url'])
        if (m != None):
           gd = m.groupdict()
           job = {}
           job['title'] = info['title']
           job['id'] = gd['job_id']
           job['url'] = m.string
           self.jobs.append(job)

    def extractInfo(self, tag):
        info = {'url': '', 'title': ''}
        try:
          info['url'] = tag.get_attribute('href').encode('utf-8')
          info['title'] = tag.get_attribute('title').encode('utf-8').strip()
        finally:
          return info

    def getJobs(self, tags):
        for tag in tags:
            info = self.extractInfo(tag)
            if (info['url']!='') and (info['title']!=''):
               self.addJob(info)

    def scrape(self):
        self.driver.get(self.link)
        pagenumb = 1
        sleep(self.delay)
        while True:
          print('reading page# '+str(pagenumb))
          self.getJobs(self.driver.find_elements_by_tag_name('a'))
          next_page_elem = self.driver.find_element_by_id('next')
          next_page_class = next_page_elem.get_attribute('class')
          print(next_page_class) #class on last page: 'navigation-link-disabled'
          if (next_page_class == '') and ((pagenumb < self.maxpage) or (self.maxpage == 0)):
              next_page_elem.click()
              pagenumb += 1
              sleep(self.delay)
          else:
              break
        print(self.jobs)
        self.driver.quit()

if __name__ == '__main__':
    scraper = Scraper()
    scraper.scrape()