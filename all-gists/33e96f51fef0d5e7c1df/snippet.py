#!/usr/bin/env python
#-*- coding: utf-8 -*-

# RescueTime Data Exporter
# Dan Nixon
# 18/09/2011

import urllib

apiKey = "API_KEY"
fileDirectory = ""
filePrefix = "RescueTimeData"

def main():
    print "RescueTime Data Exporter"
    print "Dates in format YYYY-MM-DD"
    date_s = raw_input("Start Date: ")
    date_e = raw_input("End Date: ")
    print "Getting Data for Interval", date_s, "to", date_e
    params = urllib.urlencode({'key':apiKey, 'perspective':'interval', 'format':'csv', 'restrict_begin':date_s, 'restrict_end':date_e})
    u = urllib.urlopen("http://www.rescuetime.com/anapi/data", params)
    CSVdata = u.read()
    filePath = fileDirectory + filePrefix + date_s.replace("-", "") + "-" + date_e.replace("-", "") + ".csv"
    f = open(filePath, "w")
    f.write(CSVdata)
    f.close()
    print "Data Saved to", filePath
    print ""

main()