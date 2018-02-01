from lxml import etree
import sys
import bz2
import unicodedata
 
TAG = '{http://www.mediawiki.org/xml/export-0.8/}text'
 
def fast_iter(context, func, *args, **kwargs):
    # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    # Author: Liza Daly
    # modified to call func() only in the event and elem needed
    for event, elem in context:
        if event == 'end' and elem.tag == TAG:
            func(elem, *args, **kwargs)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context
 
def process_element(elem, fout):
        global counter
        normalized = unicodedata.normalize('NFKD', \
                unicode(elem.text)).encode('ASCII','ignore').lower()
        print >>fout, normalized.replace('\n', ' ')
        if counter % 10000 == 0: print "Doc " + str(counter)
        counter += 1
 
def main():
    fin = bz2.BZ2File(sys.argv[1], 'r')
    fout = open('2013_wikipedia_en_pages_articles.txt', 'w')
    context = etree.iterparse(fin)
    global counter
    counter = 0
    fast_iter(context, process_element, fout)
 
if __name__ == "__main__":
    main()