#!/usr/bin/python
#encoding:utf-8

import stompy
import time
import curses

def monitor_stompserver():
    try:
        myscreen = curses.initscr()
        s = stompy.Stomp("127.0.0.1", port=61613)
        s.connect()
        s.subscribe({'destination':'/queue/monitor'})
        while True:
            try:
                m = s.poll()
            except:
                m = None
            queues = []
            if m != None:
                lines = m.as_string().split()
                for i in range(0,(len(lines)-5)/8):
                    queue_name = lines[i*8+5+1]
                    queue_messages = "%s messages" % lines[i*8+5+3]
                    queue_counts = "%s/%s dequeued" % (lines[i*8+5+5], lines[i*8+5+7])
                    dequeued_percentage = (float(lines[i*8+5+5])/float(lines[i*8+5+7])) * 100
                    queue_percentage = "%0.2f" % dequeued_percentage
                    queues.append([queue_name, queue_messages, queue_counts, queue_percentage])
                for j in range(len(queues)):
                    myscreen.addstr(j, 0, "%s" % queues[j][0])
                    myscreen.addstr(j, 45, "%s" % queues[j][1])
                    myscreen.addstr(j, 60, "%s" % queues[j][2])
                    myscreen.addstr(j, 85, "%s%s" % (queues[j][3], "%"))
            myscreen.refresh()
            time.sleep(5)
    except KeyboardInterrupt:
        curses.endwin()
        print "Bye!"
        exit()

if __name__ == '__main__':
    monitor_stompserver()
