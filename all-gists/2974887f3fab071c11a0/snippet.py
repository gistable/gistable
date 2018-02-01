#!/usr/bin/python
#-*- coding: utf-8 -*-

# Install
# apt-get install xvfb python-imaging (firefox or chromium-chromedriver)
# pip install selenium pyvirtualdisplay boto

import sys
import os
import socket
import logging
import datetime
import time
import httplib

from cStringIO import StringIO
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from pyvirtualdisplay.xvfb import XvfbDisplay
from PIL import Image
from boto import ses

reload(sys)
sys.setdefaultencoding("utf-8")
socket.setdefaulttimeout(60)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('shaco')


#######################
# CONFIGURATIONS START
#######################
ZABBIX_HOST = 'http://127.0.0.1'
ZABBIX_USERNAME = ''
ZABBIX_PASSWORD = ''

SCREEN_URL_FORMAT = '/'.join([ZABBIX_HOST, 'screens.php?fullscreen=1&elementid={}&period=604800&stime={}'])

FROM = 'example@example.com'
SUBJECT_FORMAT = '[Shaco] {} System Statistics - {} to {}'

TARGET = (
    {
        'name': 'Example',
        'to': ['example@example.com',],
        'elementid': 32
    },
)

ALARM_SENDER = 'alarm@sender.com'
ALARM_RECEIVER = 'alarm@receiver.com'

AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''
#######################
# CONFIGURATIONS END
#######################


class Rectangle():
    def __init__(self, left, upper, right, lower):
        self.left = left
        self.upper = upper
        self.right = right
        self.lower = lower

    def __str__(self):
        return '({}, {}, {}, {})'.format(self.left, self.upper, self.right, self.lower)

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.lower - self.upper


class Shaco():
    browser = None
    display = None

    def __init__(self):
        self.display = XvfbDisplay(size=(1024, 768)).start()

        # Firefox
        self.browser = webdriver.Firefox()

        # Chrome
        #CHROMIUM_PATH = '/usr/lib/chromium-browser'
        #os.environ['LD_LIBRARY_PATH'] = ':'.join(['/'.join([CHROMIUM_PATH, '/libs']), os.environ.get('LD_LIBRARY_PATH', '.')])
        #self.browser = webdriver.Chrome(executable_path='/'.join([CHROMIUM_PATH, 'chromedriver']))


    def __del__(self):
        if self.browser: self.browser.quit()
        if self.display: self.display.stop()

    def do(self, name):
        self.login()
        ses_conn = ses.connection.SESConnection(AWS_ACCESS_KEY, AWS_SECRET_KEY)

        sdate = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        edate = sdate + datetime.timedelta(days=6)
        stime = sdate.strftime('%Y%m%d000000')

        for target in TARGET:
            if name:
                if name != target['name']: pass

            for trycnt in range(3):
                try:
                    url = SCREEN_URL_FORMAT.format(target['elementid'], stime)
                    self.browser.get(url)
                    self.browser.find_element_by_id('iframe').click()
                    screenshot = self.get_screenshot()

                    msg = MIMEMultipart()
                    msg['From'] = FROM
                    msg['Subject'] = SUBJECT_FORMAT.format(target['name'], sdate.strftime('%Y%m%d'), edate.strftime('%Y%m%d'))
                    msg['To'] = ','.join(target['to'])

                    text = MIMEText('URL: {}'.format(url))
                    msg.attach(text)

                    img = MIMEImage(screenshot, name='{}_{}-{}.png'.format(target['name'], sdate.strftime('%Y%m%d'), edate.strftime('%Y%m%d')))
                    msg.attach(img)

                    ses_conn.send_raw_email(msg.as_string())
                    break
                except socket.timeout as e:
                    exception_handler()
                    time.sleep(30)
                    pass
                except httplib.CannotSendRequest:
                    exception_handler()
                    time.sleep(30)
                    pass
                except:
                    exception_handler()
                    raise
            else:
                ses_alarm('[Shaco] {} Statistics Report Failed!'.format(target['name']))


    def login(self):
        self.browser.get('/'.join([ZABBIX_HOST, '']))
        if self.browser.current_url.endswith('dashboard.php'): return None

        self.browser.find_element_by_id('name').send_keys(ZABBIX_USERNAME)
        self.browser.find_element_by_id('password').send_keys(ZABBIX_PASSWORD)
        self.browser.find_element_by_id('enter').click()


    def get_screenshot(self):
        if isinstance(self.browser, webdriver.Firefox):
            return self.get_screenshot_with_firefox()
        elif isinstance(self.browser, webdriver.Chrome):
            return self.get_screenshot_with_chrome()
        else:
            raise Exception('Unknown webdriver!')


    def get_screenshot_with_firefox(self):
        im = Image.open(StringIO(self.browser.get_screenshot_as_png()))
        stream = StringIO()
        im.save(stream, 'png')
        screenshot = stream.getvalue()
        stream.close()
        return screenshot

    def get_screenshot_with_chrome(self):
        totalWidth = self.browser.execute_script('return document.documentElement.scrollWidth');
        totalHeight = self.browser.execute_script('return document.documentElement.scrollHeight');

        viewportWidth = self.browser.execute_script('return document.documentElement.clientWidth');
        viewportHeight = self.browser.execute_script('return document.documentElement.clientHeight');

        rectangles = []
        for y in range(0, totalHeight, viewportHeight):
            newHeight = viewportHeight
            if (y + viewportHeight) > totalHeight:
                newHeight = totalHeight - y

            for x in range(0, totalWidth, viewportWidth):
                newWidth = viewportWidth
                if (x + viewportWidth) > totalWidth:
                    newWidth = totalWidth - x

                rectangle = Rectangle(x, y, x+newWidth, y+newHeight)
                rectangles.append(rectangle)


        im = Image.new('RGB', (totalWidth, totalHeight))
        prevRectangle = None
        for rectangle in rectangles:
            if prevRectangle:
                xDiff = rectangle.right - prevRectangle.right
                yDiff = rectangle.lower - prevRectangle.lower
                self.browser.execute_script('window.scrollBy({}, {})'.format(xDiff, yDiff))

            part = Image.open(StringIO(self.browser.get_screenshot_as_png()))
            part = part.crop((0, 0, viewportWidth, viewportHeight))
            box = (rectangle.right - part.size[0], rectangle.lower - part.size[1], rectangle.right, rectangle.lower)
            im.paste(part, box)

            prevRectangle = rectangle

        stream = StringIO()
        im.save(stream, 'png')
        screenshot = stream.getvalue()
        stream.close()
        return screenshot


def exception_handler():
    import sys, traceback
    exc_type, exc_value, exc_traceback = sys.exc_info()
    subject = '[Shaco] {}: {}'.format(exc_type, exc_value)
    ses_alarm(subject, traceback.format_exc())


def ses_alarm(subject, body=None):
    if not body: body = subject

    ses_conn = ses.connection.SESConnection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
    ses_conn.send_email(ALARM_SENDER, subject, body, ALARM_RECEIVER)


if __name__ == '__main__':
    shaco = None
    name = None

    if len(sys.argv) >= 2:
        name = sys.argv[1]

    try:
        shaco = Shaco()
        shaco.do(name)
    except Exception:
        exception_handler()
        raise
    finally:
        del shaco
