'''
redis_search.py

Written by Josiah Carlson July 3, 2010

Released into the public domain.


This module implements a simple TF/IDF indexing and search algorithm using
Redis as a datastore server.  The particular algorithm implemented uses the
standard TF/IDF scoring of (using Python notation):

    sum((document.count(term) / len(document)) *
         log(index.doc_count() / len(index.docs_with(term)), 2)
         for term in terms)

The blog post discussing the development of this Gist:
http://dr-josiah.blogspot.com/2010/07/building-search-engine-using-redis-and.html

'''

import collections
import math
import os
import re
import unittest

import redis

NON_WORDS = re.compile("[^a-z0-9' ]")

# stop words pulled from the below url
# http://www.textfixer.com/resources/common-english-words.txt
STOP_WORDS = set('''a able about across after all almost also am among
an and any are as at be because been but by can cannot could dear did
do does either else ever every for from get got had has have he her
hers him his how however i if in into is it its just least let like
likely may me might most must my neither no nor not of off often on
only or other our own rather said say says she should since so some
than that the their them then there these they this tis to too twas us
wants was we were what when where which while who whom why will with
would yet you your'''.split())

class ScoredIndexSearch(object):
    def __init__(self, prefix, *redis_settings):
        # All of our index keys are going to be prefixed with the provided
        # prefix string.  This will allow multiple independent indexes to
        # coexist in the same Redis db.
        self.prefix = prefix.lower().rstrip(':') + ':'

        # Create a connection to our Redis server.
        self.connection = redis.Redis(*redis_settings)

    @staticmethod
    def get_index_keys(content, add=True):
        # Very simple word-based parser.  We skip stop words and single
        # character words.
        words = NON_WORDS.sub(' ', content.lower()).split()
        words = [word.strip("'") for word in words]
        words = [word for word in words
                    if word not in STOP_WORDS and len(word) > 1]
        # Apply the Porter Stemmer here if you would like that functionality.

        # Apply the Metaphone/Double Metaphone algorithm by itself, or after
        # the Porter Stemmer.

        if not add:
            return words

        # Calculate the TF portion of TF/IDF.
        counts = collections.defaultdict(float)
        for word in words:
            counts[word] += 1
        wordcount = len(words)
        tf = dict((word, count / wordcount)
                    for word, count in counts.iteritems())
        return tf

    def _handle_content(self, id, content, add=True):
        # Get the keys we want to index.
        keys = self.get_index_keys(content)
        prefix = self.prefix

        # Use a non-transactional pipeline here to improve performance.
        pipe = self.connection.pipeline(False)

        # Since adding and removing items are exactly the same, except
        # for the method used on the pipeline, we will reduce our line
        # count.
        if add:
            pipe.sadd(prefix + 'indexed:', id)
            for key, value in keys.iteritems():
                pipe.zadd(prefix + key, id, value)
        else:
            pipe.srem(prefix + 'indexed:', id)
            for key in keys:
                pipe.zrem(prefix + key, id)

        # Execute the insertion/removal.
        pipe.execute()

        # Return the number of keys added/removed.
        return len(keys)

    def add_indexed_item(self, id, content):
        return self._handle_content(id, content, add=True)

    def remove_indexed_item(self, id, content):
        return self._handle_content(id, content, add=False)

    def search(self, query_string, offset=0, count=10):
        # Get our search terms just like we did earlier...
        keys = [self.prefix + key
                    for key in self.get_index_keys(query_string, False)]

        if not keys:
            return [], 0

        def idf(count):
            # Calculate the IDF for this particular count
            if not count:
                return 0
            return max(math.log(total_docs / count, 2), 0)

        total_docs = max(self.connection.scard(self.prefix + 'indexed:'), 1)

        # Get our document frequency values...
        pipe = self.connection.pipeline(False)
        for key in keys:
            pipe.zcard(key)
        sizes = pipe.execute()

        # Calculate the inverse document frequencies...
        idfs = map(idf, sizes)

        # And generate the weight dictionary for passing to zunionstore.
        weights = dict((key, idfv)
                for key, size, idfv in zip(keys, sizes, idfs) if size)

        if not weights:
            return [], 0

        # Generate a temporary result storage key
        temp_key = self.prefix + 'temp:' + os.urandom(8).encode('hex')
        try:
            # Actually perform the union to combine the scores.
            known = self.connection.zunionstore(temp_key, weights)
            # Get the results.
            ids = self.connection.zrevrange(
                temp_key, offset, offset+count-1, withscores=True)
        finally:
            # Clean up after ourselves.
            self.connection.delete(temp_key)
        return ids, known

class TestIndex(unittest.TestCase):
    def test_index_basic(self):
        t = ScoredIndexSearch('unittest', 'dev.ad.ly')
        t.connection.delete(*t.connection.keys('unittest:*'))

        t.add_indexed_item(1, 'hello world')
        t.add_indexed_item(2, 'this world is nice and you are really special')

        self.assertEquals(
            t.search('hello'),
            ([('1', 0.5)], 1))
        self.assertEquals(
            t.search('world'),
            ([('2', 0.0), ('1', 0.0)], 2))
        self.assertEquals(t.search('this'), ([], 0))
        self.assertEquals(
            t.search('hello really special nice world'),
            ([('2', 0.75), ('1', 0.5)], 2))

if __name__ == '__main__':
    unittest.main()
