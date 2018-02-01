#coding:utf-8

import urllib
import BeautifulSoup
import urlparse
import time

def main():
    urlList = open("seed.txt","r").read().splitlines()
    allowDomainList = set(open("allowDomain.txt","r").read().splitlines())
    readURL = set()

    while(urlList):
        url = urlList.pop(0)
        domain = urlparse.urlparse(url)[1]
        if not domain in allowDomainList:
            continue

        encodedURL = urllib.quote_plus(url)
        if encodedURL in readURL:
            continue

        readURL.add(encodedURL)

        # URLをGET
        try:
            urlpointer = urllib.urlopen(url)
            contentsType = urlpointer.headers["Content-Type"]
            if (contentsType.find("text/html") == -1 and
                contentsType.find("text/xml") == -1):
                print "not html contents" , contentsType
                continue

            data = urlpointer.read()
            filename = "./data/" + encodedURL

            fp = open(filename, "w")
            fp.write(data)
            fp.close()
            print url
        except:
            print "cantLoadContents"
            continue

        # SOUP化する
        try:
            soup = BeautifulSoup.BeautifulStoneSoup(unicode(data, "utf-8", "ignore"))
        except:
            print "cantCreateSoup"
            continue

        #リンク抽出
        for item in soup.findAll("a"):
            if item.has_key("href"):
                foundURL = urlparse.urljoin(url, item["href"])
                domain = urlparse.urlparse(foundURL)[1]

                if not domain in allowDomainList:
                    continue

                if urllib.quote_plus(foundURL) in readURL:
                    continue

                urlList.append(foundURL)

        time.sleep(1)

if __name__ == "__main__":
    main()