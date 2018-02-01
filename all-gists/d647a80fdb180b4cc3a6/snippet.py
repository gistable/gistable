#!/usr/bin/python
'''
Script to monitor live streams and send an Amazon SNS if the stream is down (and possibly take restorative action)

Future:
 Black detect: ffmpeg -i out.mp4 -vf blackdetect -f null -
 Note the following doesn't seem to fully work without looking at the debug logs
 On live ffmpeg -y -i rtmp://cp30129.live.edgefcs.net/live/videoops-videoops@50541 -vf blackdetect -t 10 -loglevel debug -f null -

'''

from boto import boto
import sys
import os
from subprocess import PIPE, Popen
from threading  import Thread
import time
import logging

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x



logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("encoder.log"),
                              logging.StreamHandler()])

logging.info("Starting")

# You will need to go into your Amazon Console and create a new topic ARN for this
AWS_TOPIC_ARN = ""
AWS_KEY = ""
AWS_SECRET = ""
# Set how often you want to check in seconds
SLEEP_TIME = 30
FFPROBE = "/usr/local/bin/ffprobe"

# List of streams to check
CHECK_STREAMS = ['http://wowsyd.sinclairmediatech.com/live/canberra/playlist.m3u8', 'http://repackage.video.news.com.au/live/canberra/playlist.m3u8']

ON_POSIX = 'posix' in sys.builtin_module_names

def process_line(std, q):
    partialLine = ""
    tmpLines=[]
    end_of_message = False
    while (True):
        data = std.read(10)
        
        #print repr(data)
        
        #break when there is no more data
        if len(data) == 0:
            end_of_message = True

        #data needs to be added to previous line
        if ((not "\n" in data) and (not end_of_message)):
            partialLine += data
        #lines are terminated in this string
        else:
            tmpLines = []

            #split by \n
            split = data.split("\n")

            #add the rest of partial line to first item of array
            if partialLine != "":
                split[0] = partialLine + split[0]
                partialLine = ""

            #add every item apart from last to tmpLines array
            if len(split) > 1:
                for i in range(len(split)-1):
                    tmpLines.append(split[i])

            #last item is '' if data string ends in \r
            #last line is partial, save for temporary storage
            if split[-1] != "":
                partialLine = split[-1]
            #last line is terminated
            else:
                tmpLines.append(split[-1])
            
            #print split[0]
            q.put(split[0])
            if (end_of_message):
                #print partialLine
                break

def enqueue_output(stdout, queue):
    #for line in iter(stdout.readline, b''):
    #    queue.put(line)
    process_line(stdout, queue)  
    stdout.close()

def run(q, ffcmd, thread_name):
    logging.info("Running " + ffcmd)
    p = Popen(ffcmd,shell=True, stderr=PIPE, stdin=PIPE, bufsize=1, close_fds=ON_POSIX)
    #q = Queue()
    #t = Thread(target=enqueue_output, args=(p.stdout, q))
    #t.daemon = True # thread dies with the program
    #t.start()
    t = Thread(target=enqueue_output, name=thread_name, args=(p.stderr, q))
    t.daemon = True
    t.start()
    return p
         
def probe(stream):
    probeq = Queue()
    logging.info("Checking " + stream)
    probeproc = run(probeq, FFPROBE + " " + stream, "probethread")
    # Need to read from the queue until the queue is empty and process has exited
    while (True):
        #print "Queue not empty"
#        print probeq.join()
        try:
            line = probeq.get_nowait()
            logging.info(line)
            '''
            Possible error responses:
            Server error: Failed to play stream
            Input/output error
            
            Need a regex to match for video found!
            Sample: Stream #0:0: Video: h264 (Baseline), yuv420p, 640x360 [SAR 1:1 DAR 16:9], 655 kb/s, 25 tbr, 1k tbn, 50 tbc
            Should also look for audio
            '''
           
            if ("Stream #0:0: Video" in line):
                logging.info("Found stream " + stream)
                logging.info(line)
                return True
            if ("Stream #0:1: Video" in line):
                logging.info("Found stream " + stream)
                logging.info(line)
                return True
            elif ("error" in line):
                return False
            elif (probeproc.poll() > 0):
                return False
            
            # Make sure we don't spin out of control
            #time.sleep(1)
            
        except Empty:
            pass
        
    
    return False

def send_message(msg):
    sns = boto.connect_sns(aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET)
    print sns
    subj = "Problem with streaming"
    res = sns.publish(AWS_TOPIC_ARN, msg, subj)
    

def live_probe():
    pass

# Endless loop for monitoring

while(True):
    for stream in CHECK_STREAMS:
        if (probe(stream)):
            pass
        else:
            logging.info("Error with " + stream + " sending alert")
            '''
            This needs to check if there has already been an error message sent
            If so it shouldn't send another one for x mins
            Also needs to send a message when the problem is cleared
            '''
            send_message(stream)
            
    time.sleep(SLEEP_TIME)