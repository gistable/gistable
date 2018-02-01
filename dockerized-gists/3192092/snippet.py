#coding: utf-8
import urllib2
def main():
    for i in xrange(1, 264055420):
        #http://dl.dropbox.com/u/26405542/index.html
        url = "http://dl.dropbox.com/u/%d/index.html" % i
        try:
            handle = urllib2.urlopen(url)
            data = handle.read()
            fp = open("%d_index.html" % i, "wb")
            fp.write(data)
            fp.close()
            print i, "OK"
        except:
            #print i, "NG"
            continue
if __name__ == '__main__':
    main()
