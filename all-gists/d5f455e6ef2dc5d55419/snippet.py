#!/usr/bin/python
#stolen and modified from the reddit post about the raspbeery pi tweeting at comcast
#run this every 10 minutes (or w/e) with cron:
#"crontab -e"
#*/10 * * * * /home/pi/lolbandwidth.py
import os
import sys
import csv
import datetime
import time

def test():
        #run speedtest-cli
        print 'running test'
        #install with "pip install speedtest-cli"
        csvlog = '/home/pi/speed_data.csv'
        a = os.popen("speedtest-cli --simple").read()
        print 'ran'
        #split the 3 line result (ping,down,up)
        lines = a.split('\n')
        print a
        ts = time.time()
        date =datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        #if speedtest could not connect set the speeds to 0
        if "Cannot" in a:
                p = 100
                d = 0
                u = 0
        #extract the values for ping down and up values
        else:
                p = lines[0][6:11]
                d = lines[1][10:14]
                u = lines[2][8:12]
        print date,p, d, u
        #save the data to file for local network plotting
        out_file = open(csvlog, 'a')
        writer = csv.writer(out_file)
        writer.writerow((ts*1000,p,d,u))
        out_file.close()
        return
        
if __name__ == '__main__':
        test()
        print 'completed'
