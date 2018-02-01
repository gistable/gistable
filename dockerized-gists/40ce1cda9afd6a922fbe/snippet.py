#!/usr/bin/env python
#Reddit XSS
#Author: Cheetz
import urllib2, sys
import logging, os, re, sys, urllib, string
from optparse import OptionParser
from urlparse import urlparse

class Lookup:
        def run(self,url):
                request = urllib2.Request(url)
                request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7 (.NET CLR 3.5.30729)')
                response = urllib2.urlopen(request)
                resolve_response = response.read()
                self.regex(resolve_response)
                #print resolve_response
        def regex(self,resolve_response):
                file = open("output_xss.txt", 'a')
                n = re.compile(r'href=\"http.*?>', re.IGNORECASE)
                result = n.findall(resolve_response)
                for a in result:
                        
                        if ("reddit" not in a):
                                remove_string = 'href="'
                                a = a.replace(remove_string,"")
                                b = a.split('"')
                                a = b[0]
                                file.write(a.replace(remove_string,""))
                                file.write('\n')

                p = re.compile(r'count=(\d+)&amp;after=(.*?)\"', re.IGNORECASE)
                link = p.findall(resolve_response)
                next_string = "http://www.reddit.com/r/xss/?count="+link[0][0]+"&after="+link[0][1]
                file.close()
                self.run(next_string)


if __name__ == '__main__':
        url = "http://www.reddit.com/r/xss"
        app = Lookup()
        app.run(url)