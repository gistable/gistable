
import time
import urllib2
import threading
from Queue import Queue
from random import choice

def get_random_article(namespace=None):
    """ Download a random wikipiedia article"""
    try:
        url = 'http://en.wikipedia.org/wiki/Special:Random'
        if namespace != None: 
            url += '/' + namespace
        req = urllib2.Request(url, None, { 'User-Agent' : 'x'})
        page = urllib2.urlopen(req).readlines()
        return page
    except (urllib2.HTTPError, urllib2.URLError):
        print "Failed to get article"
        raise

class DocumentDownloader(threading.Thread):
    """ A class to download a user's top Artists

    To be used as an individual thread to take
    a list of users from a shared queue and 
    download their top artists 
    """

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.articles = []
        self.queue = queue

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def get_articles(self):
        return self.articles

    def run(self):
        while True:
            if self.stopped():
                return
            if self.queue.empty(): 
                time.sleep(0.1)
                continue
            try:
                namespace = self.queue.get()
                #article = get_random_article(namespace)
                article = get_random_article()
                self.articles.append(article)
                print "Successfully processed namespace: ", namespace,
                print " by thread: ", self.ident
                # No need for a 'queue.task_done' since we're 
                # not joining on the queue
            except:
                print "Failed to process namespace: ", namespace


def get_random_documents(num_documents, num_threads=4):
    """ Download 'num_documents' random documents from
    the lastfm api.
    Each document contains the top artists for a random
    user from LastFM.
    These documents are downloaded in parallel using
    separate threads

    """

    wiki_namespaces = """
    Main
    User
    Wikipedia
    File
    MediaWiki
    Template
    Help
    Category
    Portal
    Book""".split()

    q = Queue()
    threads = []

    try:
        # Create the threads and 'start' them.
        # At this point, they are listening to the
        # queue, waiting to consume
        for i in xrange(num_threads):
            thread = DocumentDownloader(q)
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)

        # We want to download one page for each namespace,
        # so we put every namespace in the queue, and
        # these will be processed by the threads
        for i in xrange(num_documents):
            namespace = choice(wiki_namespaces)
            q.put(namespace)

        # Wait for all entries in the queue
        # to be processed by our threads
        # One could do a queue.join() here, 
        # but I prefer to use a loop and a timeout
        while not q.empty():
            time.sleep(1.0)

        # Terminate the threads once our
        # queue has been fully processed
        for thread in threads:
            thread.stop()
        for thread in threads:
            thread.join()

    except:
        print "Main thread hit exception"
        # Kill any running threads
        for thread in threads:
            thread.stop()
        for thread in threads:
            thread.join()
        raise

    # Collect all downloaded documents
    # from our threads
    documents = []
    for thread in threads:
        documents.extend(thread.get_articles())

    return documents


if __name__ == "__main__":
    documents = get_random_documents(10)
    for document in documents:
        print document[:10]
