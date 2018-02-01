"""
"""

import multiprocessing
import boto
import os
import sys
import datetime
import logging
import Queue

class Downloader(object):

    def __init__(self, download_path, bucket_name, num_processes=2,
                 log_file=None, log_level=logging.INFO):
        self.download_path = download_path
        self.bucket_name = bucket_name
        self.num_processes = num_processes
        if log_file:
            boto.set_file_logger('boto-downloader', log_file, log_level)
        else:
            boto.set_stream_logger('boto-downloader', log_level)
        self.task_queue = multiprocessing.JoinableQueue()
        self.s3 = boto.connect_s3()
        self.bucket = self.s3.lookup(self.bucket_name)
        self.n_tasks = 0

    def queue_tasks(self):
        for key in self.bucket:
            self.task_queue.put(key.name)
            self.n_tasks += 1

    def worker(self, input):
        print 'Starting worker'
        while 1:
            try:
                key_name = input.get(True, 1)
            except Queue.Empty:
                p_name =  multiprocessing.current_process().name
                boto.log.info('%s has no more tasks' % p_name)
                break
            key = self.bucket.lookup(key_name)
            path = os.path.join(self.download_path, key_name)
            try:
                key.get_contents_to_filename(path)
                input.task_done()
            except:
                boto.log.error('Unexpected error: %s', sys.exc_info()[0])
                boto.log.error('Error processing %s' % path)
                
    def main(self):
        self.queue_tasks()
        self.start_time = datetime.datetime.now()
        for i in range(self.num_processes):
            multiprocessing.Process(target=self.worker,
                                    args=(self.task_queue,)).start()
        self.task_queue.join()
        self.task_queue.close()
        self.end_time = datetime.datetime.now()
        print 'total time = ', (self.end_time - self.start_time)