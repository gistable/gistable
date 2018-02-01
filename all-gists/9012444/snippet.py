#/usr/bin/env python
# vim: set fileencoding=utf-8

from ghost import Ghost
from config import COOKIE_FILE, LOGIN_ID, LOGIN_PW
import urllib2
import cookielib
import Cookie

class NaverCrawler:
    # 새 크롤러를 만듭니다.
    def __init__(self, id, pw, displayFlag = False):
        # 새 Ghost instance를 만들어서 사용합니다.
        self.ghost = Ghost(display = displayFlag, wait_timeout = 20)
        self.currentPage = None
        self.login(id, pw)

    # 주어진 페이지를 엽니다. 이미 그 페이지에 있으면 그대로 있습니다.
    def openPage(self, url):
        if self.currentPage == url:
            return
        self.ghost.open(url)
        self.ghost.wait_for_page_loaded()
        self.currentPage = url

    # 네이버 로그인을 수행합니다.
    def login(self, id, pw):
        # 네이버 메인 페이지를 엽니다.
        self.openPage('http://www.naver.com')

        # inner frame에 들어있는 로그인 폼에 값을 채워넣고 클릭을 지시합니다.
        # 이부분은 javascript를 활용했습니다.
        self.ghost.evaluate("""
        (function() {        
          var innerDoc = document.getElementById('loginframe').contentWindow.document;
          innerDoc.getElementById('id').value = '%s';
          innerDoc.getElementById('pw').value = '%s';
          innerDoc.getElementsByClassName('btn_login')[0].click();
        })();
        """ % (id, pw), expect_loading = True)

        # 로그인 결과를 기다립니다.
        self.ghost.wait_for_selector('#query')

    def cloneCookieJar(self):
        cookieJar = cookielib.LWPCookieJar()
        self.ghost.save_cookies(cookieJar)
        return cookieJar

    # 네이버 메인 페이지에서 검색을 수행합니다.
    def main_search(self, query):
        # 네이버 메인 페이지를 엽니다.
        self.openPage('http://www.naver.com')

        self.ghost.wait_for_selector('#query')
        self.ghost.fill("#sform", { "query": query })
        self.ghost.fire_on('#sform', 'submit', expect_loading = True)

if __name__ == "__main__":
    crawler = NaverCrawler(LOGIN_ID, LOGIN_PW, False)
    cj = crawler.cloneCookieJar()
    cj.save(COOKIE_FILE)