#!python3

import imaplib
import os
import asyncio

loop = asyncio.get_event_loop()

conf = [x.strip().split() for x in open('mbsyncrc')]

get = lambda k: next(kv[1:] if len(kv) > 2 else kv[1] for kv in conf if len(kv) > 1 and kv[0] == k)

host = get('Host')
run = get('#IDLE:')
user = get('User')
passw = get('Pass')
watch = get('Patterns')

call_ = None
def run_():
    global call_
    call_ = None
    os.system("sh -c %s"%run)

class idler():
    def __init__(self, folder):
        self.folder = folder

    def start(self):
        self.imap = imaplib.IMAP4_SSL(host)
        self.imap.login(user, passw)
        self.imap.select(self.folder, readonly=True)
        self.imap.send(b"i IDLE\r\n")

    def bump(self):
        self.imap.send(b"DONE\r\n")
        done_res = self.imap.readline()
        self.imap.send(b"i IDLE\r\n")
        idle_res = self.imap.readline()
        self.schedule_wait()
        print("bumping", done_res, idle_res)

    def has_event(self):
        global call_
        line = self.imap.readline()
        if b'RECENT' in line:
            if call_: call_.cancel()
            call_ = loop.call_later(5, run_)

    def schedule(self):
        self.schedule_wait()
        self.schedule_read()

    def schedule_read(self):
        loop.add_reader(self.imap.file, self.has_event)

    def schedule_wait(self):
        loop.call_later(60 * 15, self.bump)

for folder in watch:
    print("watching", folder)
    i_ = idler(folder)
    i_.start()
    i_.schedule()

loop.run_forever()
loop.close()
