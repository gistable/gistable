from BeautifulSoup import BeautifulSoup

def _remove_attrs(soup):
    for tag in soup.findAll(True): 
        tag.attrs = None
    return soup


def example():
    doc = '<html><head><title>test</title></head><body id="foo" onload="whatever"><p class="whatever">junk</p><div style="background: yellow;" id="foo" class="blah">blah</div></body></html>'
    print 'Before:\n%s' % doc
    soup = BeautifulSoup(doc)
    clean_soup = _remove_attrs(soup)
    print '\nAfter:\n%s' % clean_soup