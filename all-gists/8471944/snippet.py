
import pytest
import elasticsearch


@pytest.fixture
def index():
    return "test_index"


@pytest.fixture
def es(request, index):
    client = elasticsearch.Elasticsearch()

    def fin():
        client.indices.delete(index=index)

    request.addfinalizer(fin)
    return client


@pytest.fixture
def doc_type():
    return "test_doc_type"


@pytest.fixture
def doc(es, index, tags, doc_type):

    body = {
        "name": "Test title",
        "tags": tags
    }
    es.index(
        index=index,
        doc_type=doc_type,
        id=1,
        body=body,
    )
    es.indices.flush(index=index)
    return body


@pytest.mark.parametrize(
    ('tags', 'search_tags'),
    (
        (['hello', 'world'], ['hello']),
        (['hello', 'world'], ['world']),
        (['hello', 'world'], ['hello', 'world']),
        (['hello', 'world'], ['world', 'hello']),
        (['1', 'hello', 'world'], ['world']),
        (['1', 'hello', 'world'], ['1']),
        (['aa', 'hello', 'world'], ['hello']),
        (['aa', 'hello', 'world'], ['aa']),
        (['b', 'hello', 'world'], ['b']),
        (['a', 'hello', 'world'], ['a']),
    )
)
def test_filter(es, index, doc, doc_type, search_tags):
    # do a get
    res = es.get(index=index, doc_type=doc_type, id=1)
    assert res["_source"] == doc

    res = es.search(
        index=index,
        doc_type=doc_type,
        body={
            'query': {
                'filtered': {
                    'filter': {
                        'terms': {'tags': search_tags},
                    },
                },
            },
        },
    )
    assert res["hits"]["hits"][0]["_source"] == doc
