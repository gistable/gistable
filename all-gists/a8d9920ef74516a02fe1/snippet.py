>>> import itertools
>>> import string
>>> from elasticsearch import Elasticsearch,helpers
es = Elasticsearch()
>>> # k is a generator expression that produces
... # a series of dictionaries containing test data.
... # The test data are just letter permutations
... # created with itertools.permutations.
... #
... # We then reference k as the iterator that's
... # consumed by the elasticsearch.helpers.bulk method.
>>> k = ({'_type':'foo', '_index':'test','letters':''.join(letters)}
...      for letters in itertools.permutations(string.letters,2))

>>> # calling k.next() shows examples
... # (while consuming the generator, of course)
>>> # each dict contains a doc type, index, and data (at minimum)
>>> k.next()
{'_type': 'foo', 'letters': 'ab', '_index': 'test'}
>>> k.next()
{'_type': 'foo', 'letters': 'ac', '_index': 'test'}
>>> # create our test index
>>> es.indices.create('test')
{u'acknowledged': True}
>>> helpers.bulk(es,k)
(2650, [])
>>> # check to make sure we got what we expected...
>>> es.count(index='test')
{u'count': 2650, u'_shards': {u'successful': 1, u'failed': 0, u'total': 1}}