# -*- coding: utf-8 -*-

import os
from Queue import Queue
from threading import Thread


class FileDownloader(Thread):
    """Threaded file downloader."""
    def __init__(self, infos_tuple):
        # infos_tuple is a 2-tuples tuple containing the file url and
        # the local path to save the file to
        self.url, self.local_file = infos_tuple
        self.result = None
        super(FileDownloader, self).__init__()

    def run(self):
        try:
            if os.path.exists(self.local_file):
                # do nothing if we already have the file locally
                self.result = (self.local_file, True)
                return
            # create parent folders if needed
            local_dir = os.path.split(self.local_file)[0]
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            # download and save file
            response = urlopen(self.url)
            with open(self.local_file, 'wb+') as f:
                f.write(response.read())
        except Exception as err:
            self.result = (self.local_file, False)
            return
        self.result = (self.local_file, True)


class MultiFileDownloader(object):
    """Downloads multiple files in multiple parallels threads."""
    def __init__(self, infos_tuples, max_threads=5):
        self.infos_tuples = infos_tuples
        self.results = []
        self.queue = Queue(max_threads)

    def start(self):
        def producer():
            """Feed the queue with FileDownloader instances."""
            for infos_tuple in self.infos_tuples:
                thread = FileDownloader(infos_tuple)
                thread.start()
                self.queue.put(thread)
        def consumer():
            """Gather results from FileDownloader instances in the queue."""
            while len(self.results) < len(self.infos_tuples):
                thread = self.queue.get()
                thread.join()
                self.results.append(thread.result)
        self._tprod = Thread(target=producer)
        self._tcons = Thread(target=consumer)
        self._tprod.start()
        self._tcons.start()

    def join(self):
        self._tprod.join()
        self._tcons.join()
