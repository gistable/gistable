from toolz import concat

def page_iterator(query, page_size=999, **kwargs):
    '''
    Returns an iterator over pages of a query.
    Can be used to work-around the 1000 entity limit in remote_api_shell

    :params query:      The query we're using.
    :params page_size:  The page size to return.
    :params qwargs:     Additional options for fetch_page
    '''
    more = True
    cursor = None
    while more:
        page, cursor, more = query.fetch_page(page_size, start_cursor=cursor,
                                              **kwargs)
        if page:
            yield page


def fetch_all(query):
    '''
    Fetches all the results for a query, using page_iterator
    Should be used to work-around the 1000 entity limit in remote_api_shell.
    '''
    return list(concat(page_iterator(query)))


def count_results(query):
    '''
    Equivalent to query.count() but that works around 1000 limit.
    '''
    return reduce(lambda total, r: total + len(r),
                  page_iterator(query, keys_only=True), 0)
