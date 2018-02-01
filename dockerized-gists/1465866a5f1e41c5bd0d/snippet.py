#!/usr/bin/env python
# coding: utf-8

"""
grspider.py ----- A spider to get gnma remic prospectuses list
author: Leslie Zhu
email: pythonisland@gmail.com
In GNMA Agency webiste http://www.ginniemae.gov/, there are some remic prospectuses published by month.
Like url :
http://www.ginniemae.gov/doing_business_with_ginniemae/investor_resources/prospectuses/Pages/remic_prospectuses.aspx
There is the latest month's remic prospectuses, but there is only No. 1~10 files, the No. 11~20 and No. 21~30 need to
click a button which based on JavaScript call.
And check each page's content, we will get the JavaScript's url pattern:
- <a href="javascript: __doPostBack('ctl00$m$g_01259610_86e5_4c21_9a20_5a2b7d94350f','dvt_firstrow={11};dvt_startposition={}');">
- <a href="javascript: __doPostBack('ctl00$m$g_01259610_86e5_4c21_9a20_5a2b7d94350f','dvt_firstrow={1};dvt_startposition={}');">
- <a href="javascript: __doPostBack('ctl00$m$g_01259610_86e5_4c21_9a20_5a2b7d94350f','dvt_firstrow={21};dvt_startposition={}');">
- <a href="javascript: __doPostBack('ctl00$m$g_01259610_86e5_4c21_9a20_5a2b7d94350f','dvt_firstrow={31};dvt_startposition={}');">
And the function __doPostBack():
::
    <script type="text/javascript">
    ...
    function __doPostBack(eventTarget, eventArgument) {
         if (!theForm.onsubmit || (theForm.onsubmit() != false)) {
             theForm.__EVENTTARGET.value = eventTarget;
             theForm.__EVENTARGUMENT.value = eventArgument;
             theForm.submit();
           }
    }
   </script>
"""

import requests
import re
import urllib
import urllib2
import httplib
import sys
import cookielib
import json

class GRSpider(object):
    def __init__(self,Year="Year",Month="Month"):
        self.year = Year
        self.month = Month

        self.host_url = "http://www.ginniemae.gov"
        self.search_url = self.get_url()
        print self.search_url

        self.pattern = "(/doing_business_with_ginniemae/investor_resources/Prospectuses/ProspectusesLib/.*?.pdf)"
        self.pattern_js = "javascript: __doPostBack\('(.*)','dvt_firstrow={(\d+)};dvt_startposition={}'\);"

        self.remic_data = dict()


    def check_year(self):
        if self.year == "Year":
            return self.year
        else:
            year = int(self.year)

        if year < 1994 or year > 2100:
            print "Bad year:",year
            sys.exit()
        else:
            return year

    def check_month(self):
        if self.month == "Month":
            return self.month
        else:
            month = int(self.month)
        
        if month < 1 or month > 12:
            print "Bad Month: ",month
            sys.exit()
        else:
            return month

    def get_url(self):
        base_url = "http://www.ginniemae.gov/doing_business_with_ginniemae/investor_resources/prospectuses/Pages/remic_prospectuses.aspx"

        if self.year != "Year" or self.month != "Month":
            year  =  self.check_year()
            month = self.check_month()
            month_name = self.month_name(month)
            return base_url + "?YearDropDown=%s&MonthDropDown=%s" % (year,month_name)
        else:
            return base_url

    def month_name(self,month):
        data = {
            1:'January',2:'February',3:'March',4:'April',
            5:'May',6:'June',7:'July',8:'August',
            9:'September',10:'October',11:'November',12:'December',
            'Month':"Month"
        }

        return data[month]

    def parse(self,text=""):
        
        eventTarget = ""
        eventArgument = ""

        for line in text.split('href'):
            data = re.search(self.pattern,line)
            if data:
                for i in data.groups():
                    _remic = i.strip().split('/')[-1].replace('.pdf','').split('-')
                    remic = _remic[0][:4] + '-' + _remic[1]
                    self.remic_data[remic] = self.host_url + i
                
            data = re.search(self.pattern_js,line)
            if data:
                eventTarget = data.group(1)
                eventArgument = data.group(2)

        if eventTarget != "" and eventArgument not in  ["","1"]:
            self.next_page(eventTarget,eventArgument)
        

    def next_page(self,eventTarget,eventArgument):

        cj = cookielib.LWPCookieJar()  
        cookie_support = urllib2.HTTPCookieProcessor(cj)  
        opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)  
        urllib2.install_opener(opener)         
        
        urllib2.urlopen(self.search_url)
        
        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1',  
            'Referer' : self.search_url
        } 
        
        
        data = {
            '__EVENTTARGET': eventTarget,
            '__EVENTARGUMENT': 'dvt_firstrow={%s};dvt_startposition={}' % eventArgument,
        }
        
        postData = urllib.urlencode(data)
        request = urllib2.Request(self.search_url, postData, headers)
        response = urllib2.urlopen(request)
        text = response.read() 
        self.parse(text)
    

    def display(self):
        for remic in sorted(self.remic_data):
            print remic,self.remic_data[remic]

    def dump(self):
        w = open("gnma_remic.json","w")
        w.write(json.dumps(self.remic_data, sort_keys=True,indent=4, separators=(',', ': ')))
        w.close()

    def run(self):
        r =requests.get(self.search_url)        
        if r.status_code != 200:
            print self.search_url,r.status_code
            sys.exit()
        else:
            self.parse(r.text)




def main():     
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-y', '--year', dest = 'year', type = 'string', default = 'Year', help = 'The year of prospectuses')
    parser.add_option('-m', '--month', dest = 'month', type = 'string', default = 'Month', help = 'The month of prospectuses')

    (opts, args) = parser.parse_args()

    grspider = GRSpider(opts.year, opts.month)
    grspider.run()
    grspider.dump()


if __name__ == "__main__":
    import sys
    sys.exit(main())