from HTMLParser import HTMLParser
import urllib2

class GetTitle(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.title_flag = False

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.title_flag = True

    def handle_data(self, data):
        if self.title_flag:
            self.title = data
            self.title_flag = False

def main():
    url = 'http://twitter.com'
    response = urllib2.urlopen(url)
    gt = GetTitle()
    gt.feed(response.read())
    gt.close()
    print '%s - %s' % (url, gt.title)

if __name__ == '__main__':
    main()