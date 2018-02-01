if __name__=='__main__':
    import urllib, os, sys
    link=sys.argv[1]
    print "opening url:", link
    site = urllib.urlopen(link)
    meta = site.info()
    print "Content-Length:", meta.getheaders("Content-Length")[0]