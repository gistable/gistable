# requires twill==0.9
import sys
from twill import get_browser
from pprint import pprint

class PdfFinder:
    browser = None
    _b = None
    _q = None
    links = {}

    def __init__(self):
        self.browser = get_browser()
        self.browser.go('http://it-ebooks.info')
        self._b = self.browser._browser
        self._q = list(self._b.forms())[0]['q']

    def search(self,term):
        self.browser.get_form(1).set_value(term,'q')
        self.browser.get_form(1).set_value(['title'],'type')
        self.browser.submit('None')
        self.links = {
                x.text.split('\xe2\x86\x92')[0].strip():x for x in list(
                    self._b.links()
                ) if 'book/' in x.url or '/search' in x.url
        }
        #print [x[1].attrs[-1][1].strip() for x in self.links.items()]
        while 'Next page' in [x[1].attrs[-1][1].strip() for x in self.links.items()]:
            self.get_link(self.links.pop('Next'))
            self.links.update({
                str(x.text.split('\xe2\x86\x92')[0].strip()):x for x in list(
                    self._b.links()
                ) if 'book/' in x.url or '/search' in x.url
            })
        return '\n'.join(map(str,['{} {}'.format(n,x) for n,x in enumerate(self.links.keys())]))

    def get_link(self,link):
        self.browser.follow_link(link)

    def get_links(self):
        return '\n'.join(map(str,[x.url for x in list(self.browser._browser.links())]))

    def get_dl_link(self):
        return [x for x in list(self.browser._browser.links()) if 'filepi' in x.url][0]

    def save_file(self,name):
        f = open(name,'wb')
        f.write(self.browser.result.page)
        f.close()

    def make_filename(self):
        name,junk,ext = map(str.strip,self.browser.get_title().split('-'))
        return str(name.replace(' ','_').replace('-','_').replace(',','') + '.' + ext).lower()
        
def print_usage():
    print 'Usage: findpdf <TERM> <NUM> [outfile] - search for TERM and download NUM'
    sys.exit()

def main():
    finder = PdfFinder()
    if any(filter(lambda x: x=='-h' or x=='--help',sys.argv)):
        print_usage()
    if len(sys.argv) == 2:
        print finder.search(sys.argv[1])
    elif len(sys.argv) >= 3:
        finder.search(sys.argv[1])
        finder.get_link(finder.links[finder.links.keys()[int(sys.argv[2])]])
        name = (len(sys.argv) == 4) and sys.argv[-1] or finder.make_filename()
        finder.get_link(finder.get_dl_link())
        finder.save_file(name)
        print 'saved {} to file'.format(name)
    else:
        print_usage()
if __name__ == "__main__":
    main()