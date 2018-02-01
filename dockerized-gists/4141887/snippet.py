from functools import partial
from itertools import imap, izip, product

from redis import Redis


class SearchIndex(object):
    """Autocomplete search index.

    >>> index = SearchIndex(Redis())
    >>> index.add_item('tv_shows/twin_peaks', 'Twin Peaks', 1000)
    >>> index.search('twin')
    ('tv_shows/twin_peaks', 1000.0, 'Twin Peaks')
    """

    def __init__(self, r):
        """Initialize the index with a Redis instance."""
        self._r = r

    def _clean_words(self, title):
        """Generate normalized alphanumeric words for a given title."""
        for word in title.lower().strip().split():
            yield ''.join(c for c in word if c.isalnum())

    def _prefixes(self, title):
        """Generate the prefixes for a given title."""
        for word in self._clean_words(title):
            prefixer = partial(word.__getslice__, 0)
            for prefix in imap(prefixer, range(1, len(word) + 1)):
                yield prefix

    def add_item(self, item_id, item_title, score):
        """Add an item to the autocomplete index."""
        with self._r.pipeline() as pipe:
            for prefix in self._prefixes(item_title):
                pipe.zadd(prefix, item_id, score)
            pipe.hset('$titles', item_id, item_title)
            pipe.execute()
        return True

    def search(self, query, n=500):
        """Return the top N objects from the autocomplete index."""

        def query_score(terms, title):
            """Score the search query based on the title."""

            def term_score(term, word):
                if word.startswith(term):
                    return float(len(term)) / len(word)
                else:
                    return 0.0

            words = list(self._clean_words(title))
            return sum(term_score(t, w) for t, w in product(terms, words))

        terms = list(self._clean_words(query))
        with self._r.pipeline() as pipe:
            pipe.zinterstore('$tmp', terms, aggregate='max')
            pipe.zrevrange('$tmp', 0, n, withscores=True)
            response = pipe.execute()
            scored_ids = response[1]
        titles = self._r.hmget('$titles', *[i[0] for i in scored_ids])
        results = imap(lambda x: x[0] + (x[1],), izip(scored_ids, titles))
        return sorted(results, key=lambda r: query_score(terms, r[2]) * r[1], reverse=True)
