"""Print most frequent N-grams in given file.

Usage: python ngrams.py filename

Problem description: Build a tool which receives a corpus of text,
analyses it and reports the top 10 most frequent bigrams, trigrams,
four-grams (i.e. most frequently occurring two, three and four word
consecutive combinations).

NOTES
=====

I'm using collections.Counter indexed by n-gram tuple to count the
frequencies of n-grams, but I could almost as easily have used a
plain old dict (hash table). In that case I'd use the idiom
"dct.get(key, 0) + 1" to increment the count, and heapq.nlargest(10)
or sorted() on the frequency descending instead of the
counter.most_common() call.

In terms of performance, it's O(N * M) where N is the number of words
in the text, and M is the number of lengths of n-grams you're
counting. In this case we're counting digrams, trigrams, and
four-grams, so M is 3 and the running time is O(N * 3) = O(N), in
other words, linear time. There are various micro-optimizations to be
had, but as you have to read all the words in the text, you can't
get much better than O(N) for this problem.

On my laptop, it runs on the text of the King James Bible (4.5MB,
824k words) in about 3.9 seconds. Full text here:
https://www.gutenberg.org/ebooks/10.txt.utf-8

I haven't done the "extra" challenge to aggregate similar bigrams.
However, what I would do to start with is, after calling
count_ngrams(), use difflib.SequenceMatcher to determine the
similarity ratio between the various n-grams in an N^2 fashion. This
would be quite slow, but a reasonable start for smaller texts.

This code took me about an hour to write and test. It works on Python
2.7 as well as Python 3.x.
"""

import collections
import re
import sys
import time


def tokenize(string):
    """Convert string to lowercase and split into words (ignoring
    punctuation), returning list of words.
    """
    return re.findall(r'\w+', string.lower())


def count_ngrams(lines, min_length=2, max_length=4):
    """Iterate through given lines iterator (file object or list of
    lines) and return n-gram frequencies. The return value is a dict
    mapping the length of the n-gram to a collections.Counter
    object of n-gram tuple and number of times that n-gram occurred.
    Returned dict includes n-grams of length min_length to max_length.
    """
    lengths = range(min_length, max_length + 1)
    ngrams = {length: collections.Counter() for length in lengths}
    queue = collections.deque(maxlen=max_length)

    # Helper function to add n-grams at start of current queue to dict
    def add_queue():
        current = tuple(queue)
        for length in lengths:
            if len(current) >= length:
                ngrams[length][current[:length]] += 1

    # Loop through all lines and words and add n-grams to dict
    for line in lines:
        for word in tokenize(line):
            queue.append(word)
            if len(queue) >= max_length:
                add_queue()

    # Make sure we get the n-grams at the tail end of the queue
    while len(queue) > min_length:
        queue.popleft()
        add_queue()

    return ngrams


def print_most_frequent(ngrams, num=10):
    """Print num most common n-grams of each length in n-grams dict."""
    for n in sorted(ngrams):
        print('----- {} most common {}-grams -----'.format(num, n))
        for gram, count in ngrams[n].most_common(num):
            print('{0}: {1}'.format(' '.join(gram), count))
        print('')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python ngrams.py filename')
        sys.exit(1)

    start_time = time.time()
    with open(sys.argv[1]) as f:
        ngrams = count_ngrams(f)
    print_most_frequent(ngrams)
    elapsed_time = time.time() - start_time
    print('Took {:.03f} seconds'.format(elapsed_time))
