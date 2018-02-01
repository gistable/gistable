import urllib2
import time

s = time.time()

sources = {'week': 0, 'month': 0, 'year': 0}

for type in sources.iterkeys():
    response = urllib2.urlopen("http://www.goodreads.com/book/most_read?category=all&country=all&duration=" + type[0])
    sources[type] = response.read()

for type, source in sorted(sources.items()):
    index = [0, 0]
    count = 1
    string = 'class="bookTitle" itemprop="url"><span itemprop=\'name\'>'
    num = source.count(string)
    print "\nPopular this {0} on Goodreads (scraped on {1}):\n".format(type, time.asctime())
    for i in range(num):
        index[0] = source.find(string, index[1]) + len(string)
        index[1] = source.find('</span></a><br/>', index[0])
        if index[1] != -1:
            print "{0}. {1}".format(count, source[index[0]:index[1]])
        else: break
        count += 1
        
print "\nDone in {} seconds.\n".format(time.time()-s)