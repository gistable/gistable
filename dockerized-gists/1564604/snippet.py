#!/usr/bin/env python
# Monitor for new questions on StackOverflow
# Author: Xueqiao Xu <xueqiaoxu@gmail.com>

import time
import json
import gzip
import pprint
import urllib
import urllib2
import StringIO

import pygame
import pynotify

class Question(object):
    def __init__(self, question_dict):
        self.data = question_dict

    def __getitem__(self, key):
        return self.data.get(key, None)

    def __hash__(self):
        return self.data.get('question_id')

    def __cmp__(self, other):
        return 0


def monitor_tags(tags, interval=60):
    sound = pygame.mixer.Sound('/usr/share/sounds/purple/receive.wav')
    API_URL = 'http://api.stackoverflow.com/1.1/questions?'
    API_KEY = 'jreg2DTPcUeAcbhmnAjS_Q'
    while True:
        start_time = time.time()
        all_questions = set()
        for tag in tags:
            payload = {
                    'key': API_KEY,
                    'fromdate': int(start_time) - 60,
                    'sort': 'creation',
                    'tagged': tag
                    }
            response = urllib2.urlopen(API_URL + urllib.urlencode(payload))
            data = gzip.GzipFile(fileobj=StringIO.StringIO(response.read())).read()
            questions = map(Question, json.loads(data)['questions'])
            for question in questions: 
                all_questions.add(question)

        print len(all_questions), time.strftime('%X', time.localtime())
        if all_questions:
            header = '%d new' % len(all_questions)
            body = '\n'.join(map(lambda q: q['title'], all_questions))
            sound.play()
            pynotify.Notification(header, body).show()
                
        time.sleep(max(interval - (time.time() - start_time), 0))


def main():
    pynotify.init('1')
    pygame.mixer.init()
    monitor_tags(['javascript', 'python', 'node.js', 'jquery', 'mongodb', 'c', 'c++'])

if __name__ == '__main__':
    main()