class V2exHandler(webapp2.RequestHandler):
    def get(self, cmd):
        return
        if cmd == 'daily':
            url = 'http://v2ex.com/signin'
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31'),
                                 ('Referer', 'http://v2ex.com/signin')]
            res = opener.open(url)
            soup = BeautifulSoup(res)
            soup = soup.findAll('form')[1]
            once = soup.findAll('tr')[2].findAll('td')[1].find('input')['value']
            form = {'u' : 'iloahz', 'p' : 'xxoohowkuaile', 'next' : '/', 'once' : once}
            res = opener.open(url, urllib.urlencode(form))
            url = 'http://v2ex.com/mission/daily'
            res = opener.open(url)
            soup = BeautifulSoup(res)
            soup = soup.findAll('input')
            url = soup[1]['onclick'].split("'")[1]
            url = 'http://v2ex.com' + url.strip()
            res = opener.open(url)
            logging.info('Retrieved Successfully!')