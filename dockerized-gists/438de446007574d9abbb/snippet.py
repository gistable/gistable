#-------------------------------------------------------------------------------
# Name:        FACEBOOK TEST
# Purpose:
#
# Author:      Julius
#
# Created:     16.06.2015
# Copyright:   (c) Julius 2015
# Licence:     <APACHE>
#-------------------------------------------------------------------------------

#IMPORTS
import requests
from bs4 import BeautifulSoup

#CONSTRAINTS
EMAIL = "xyz@web.de"
PASSW = "abcdefgh"
LOGIN_URL = "https://m.facebook.com/login.php?refsrc=https%3A%2F%2Fm.facebook.com%2F&amp;refid=8"
FACEBOOK_URL = "https://m.facebook.com/"

#VARS
s = None

#MAIN CLASS
class facebook():
    def __init__(self):
        self.s = requests.session()
        self.login()

    def login(self):
        #GET DEFAULT VALUES FROM PAGE
        r = self.s.get(FACEBOOK_URL)
        soup = BeautifulSoup(r.text)
        #GET DEFAULT VALUES
        tmp = soup.find(attrs={"name": "lsd"})
        lsd = tmp.get("value")
        tmp = soup.find(attrs={"name": "charset_test"})
        csettest = tmp.get("value")
        tmp = soup.find(attrs={"name": "version"})
        version = tmp.get("value")
        tmp = soup.find(attrs={"name": "ajax"})
        ajax = tmp.get("value")
        tmp = soup.find(attrs={"name": "width"})
        width = tmp.get("value")
        tmp = soup.find(attrs={"name": "pxr"})
        pxr = tmp.get("value")
        tmp = soup.find(attrs={"name": "gps"})
        gps = tmp.get("value")
        tmp = soup.find(attrs={"name": "dimensions"})
        dimensions = tmp.get("value")
        tmp = soup.find(attrs={"name": "m_ts"})
        m_ts = tmp.get("value")
        tmp = soup.find(attrs={"name": "li"})
        li = tmp.get("value")

        data = {
            'lsd': lsd,
            'charset_test': csettest,
            'version': version,
            'ajax': ajax,
            'width': width,
            'pxr': pxr,
            'gps': gps,
            'm_ts': m_ts,
            'li': li,
        }
        data['email'] = EMAIL
        data['pass'] = PASSW
        data['login'] = 'Log In'

        r = self.s.post(LOGIN_URL , data=data)
        print r.text

fb = facebook()