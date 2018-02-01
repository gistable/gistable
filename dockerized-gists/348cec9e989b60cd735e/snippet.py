#!/usr/bin/env python
# coding=utf8
"""
Copyright (c) 2015 ServerAstra Ltd.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import print_function
import requests # This is needed
from threading import Thread
from Queue import Queue
import traceback
from requests_toolbelt.multipart.encoder import MultipartEncoderMonitor # This one not so, but you'll have to rewrite some code

from gevent import monkey # this and next line are not necessary
monkey.patch_all()


class session_connector(Thread):

    def __init__(self, session, queue):
        self.queue = queue
        self.session = session
        self.response = None
        self.headers = {'User-Agent': 'Jakarta Commons-HttpClient/3.1'}
        Thread.__init__(self)

    def progressbar(self, monitor):
        print(monitor.bytes_read / self.lengthofdata, end='\r')

    def run(self):
        while True:
            try:
                user, password, host, filedata = self.queue.get()
                self.name = host
                self.lengthofdata = len(filedata)
                payload = {'name': user, 'pwd': password}
                print('{}: Logging in'.format(self.name))
                self.response = self.session.post(
                    "http://{}/cgi/login.cgi".format(host), headers=self.headers, data=payload, timeout=10)
                if self.response.status_code == 200 and "../cgi/url_redirect.cgi?url_name=mainmenu" in self.response.text:
                    print('{}: Logged in successfully'.format(self.name))
                    opt = MultipartEncoderMonitor.from_fields(
                        fields=[('FileType', '3'), ('preserve_config', '1'),
                                ('FS_Whatever', ('SMT_X10_185.bin', filedata, 'application/octet-stream'))],
                        callback=self.progressbar
                    ) # If you change your file location don't forget to change file name as well
                    print('{}: Uploading file'.format(self.name))
                    self.response = self.session.post("http://{}/cgi/firmware_upload.cgi".format(
                        host), headers=self.headers, data=opt, timeout=360)
                    if self.response.status_code == 200 and "complete" in self.response.text:
                        print('{}: Upload successful, give us 1 minute to install and reboot'.format(
                            self.name))
            except:
                print("error")
                traceback.print_exc()
            self.queue.task_done()
        return

q = Queue()
threads = []
for i in range(30):
    session = requests.session()
    t = session_connector(session, q)
    t.daemon = True
    threads.append(t)

df = open('/root/SMT_X10_185.bin', 'r').read() # File location
obj = """
192.168.0.1
192.168.0.2
""".strip().split('\n')
for host in obj:
    q.put(('ADMIN', 'password', host, df)) # Administrator user and password

for t in threads:
    t.start()
q.join()