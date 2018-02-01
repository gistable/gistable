#!/usr/bin/python
import os
import sys
import csv
import datetime
import time
import twitter
 
def test():
 
        #run speedtest-cli
        print 'running test'
        a = os.popen("python /home/pi/speedtest/speedtest-cli --simple").read()
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
        out_file = open('/var/www/assets/data.csv', 'a')
        writer = csv.writer(out_file)
        writer.writerow((ts*1000,p,d,u))
        out_file.close()
 
        #connect to twitter
        TOKEN=""
        TOKEN_KEY=""
        CON_SEC=""
        CON_SEC_KEY=""
 
        my_auth = twitter.OAuth(TOKEN,TOKEN_KEY,CON_SEC,CON_SEC_KEY)
        twit = twitter.Twitter(auth=my_auth)
 
        #try to tweet if speedtest couldnt even connet. Probably wont work if the internet is down
        if "Cannot" in a:
                try:
                        tweet="Hey @Comcast @ComcastCares why is my internet down? I pay for 150down\\10up in Washington DC? #comcastoutage #comcast"
                        twit.statuses.update(status=tweet)
                except:
                        pass
 
        # tweet if down speed is less than whatever I set
        elif eval(d)<50:
                print "trying to tweet"
                try:
                        # i know there must be a better way than to do (str(int(eval())))
                        tweet="Hey @Comcast why is my internet speed " + str(int(eval(d))) + "down\\" + str(int(eval(u))) + "up when I pay for 150down\\10up in Washington DC? @ComcastCares @xfinity #comcast #speedtest"
                        twit.statuses.update(status=tweet)
                except Exception,e:
                        print str(e)
                        pass
        return
       
if __name__ == '__main__':
        test()
        print 'completed'