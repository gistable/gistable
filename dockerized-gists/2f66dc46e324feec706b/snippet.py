import elasticsearch
from math import log


def tfidf_matrix(es, index, doc_type, fields, size=10, bulk=500, query=dict(match_all=[])):
    """Generate tfidf for `size` documents of `index`/`doc_type`.
    All `fields` need to have the mapping "term_vector": "yes".
    This is the consuming version (i.e. get everything at once).

    :param es: elasticsearch client
    :type es: https://github.com/elasticsearch/elasticsearch-py

    :param index: the elasticsearch index
    :type index: str

    :param doc_type: the elasticsearch doc_type
    :type doc_type: str

    :param fields: the fields to be considered
    :param fields: list(str)

    :param size: the number of documents to process
    :type size: int

    :param bulk: the batch size (be nice to elasticsearch) to be processed at once
    :type bulk: int

    :param query: the query for the documents to be considered
    :type query: elasticsearch query dictionary
    """
    return {_id: matrix for _id, matrix in
            gen_tfidf_matrix(es, index, doc_type, fields, size=size, bulk=bulk, query=query)}


def gen_tfidf_matrix(es, index, doc_type, fields, size=10, bulk=500, query=dict(match_all=[])):
    """Generate tfidf for `size` documents of `index`/`doc_type`.
    All `fields` need to have the mapping "term_vector": "yes".
    This is the generator version (if you need to process one doc after each other).

    :param es: elasticsearch client
    :type es: https://github.com/elasticsearch/elasticsearch-py

    :param index: the elasticsearch index
    :type index: str

    :param doc_type: the elasticsearch doc_type
    :type doc_type: str

    :param fields: the fields to be considered
    :param fields: list(str)

    :param size: the number of documents to process
    :type size: int

    :param bulk: the batch size (be nice to elasticsearch) to be processed at once
    :type bulk: int

    :param query: the query for the documents to be considered
    :type query: elasticsearch query dictionary
    """
    for ids in gen_ids(es, index, doc_type, size, bulk, query):
        if len(ids) == 0:
            break
        for doc in gen_tv(es, index, doc_type, fields, ids):
            yield (doc['_id'], matrix(doc))


def gen_ids(es, index, doc_type, size, bulk, query):
    """Generator for lists of ids of `index`/`doc_type`.
    It returns `size` ids partitioned into ceil(`size`/`bulk`) lists.
    """
    count = 0

    if bulk > size or bulk == 0:
        bulk = size

    response = es.search(index,
                            doc_type,
                            scroll='30s',
                            body=dict(
                            query=query,
                            size=bulk,
                            fields=[])
                            )

    scroll_id = response['_scroll_id']
    count += bulk
    yield [h['_id'] for h in response['hits']['hits']]

    while count < size:
        count += bulk
        response = es.scroll(scroll_id=scroll_id, scroll='10s')
        scroll_id = response['_scroll_id']
        if len(response['hits']['hits']) == 0:
            break
        yield [h['_id'] for h in response['hits']['hits']]


def gen_tv(es, index, doc_type, fields, ids):
    for doc in es.mtermvectors(index=index,
                                    doc_type=doc_type,
                                    body=dict(
                                        ids=ids,
                                        parameters=dict(
                                            term_statistics=True,
                                            field_statistics=True,
                                            fields=fields))
                               )['docs']:
        yield doc


def matrix(tvdoc):
    """Transform elasticsearch's term vector into tfidf.
    """
    fields = lambda doc: doc['term_vectors']  # -> dict(fieldname: dict(term: vec))
    terms = lambda field: field['terms']  # -> dict(term: dict(stats))
    tf = lambda vec: vec["term_freq"]
    df = lambda vec: vec["doc_freq"]
    n_docs = lambda field: field['field_statistics']['doc_count']  # -> int (note: this is per shard!)

    return {fieldname: {
        term: tfidf(tf(vec), df(vec), n_docs(field)) for term, vec in
        terms(field).items()}
        for fieldname, field in fields(tvdoc).items()}


def tfidf(tf, df, n_docs):
    idf = log(n_docs / float(df))
    return tf * idf