>>> import pyes
>>> conn = pyes.es.ES("localhost:9200")
>>> all = conn.scan(pyes.query.MatchAllQuery(), 'index', 'type')
>>> for a in all:
...     hits = a['hits']['hits']
...     for hit in hits:
...         conn.index(hit['_source'], 'new_index', 'type', hit['_id'], bulk=True)
