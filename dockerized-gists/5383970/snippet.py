"""
Collection of query wrappers / abstractions to both facilitate data
retrieval and to reduce dependency on DB-specific API.
"""
from pandas.core.api import DataFrame


def _safe_fetch(cur):
    try:
        result = cur.fetchall()
        if not isinstance(result, list):
            result = list(result)
        return result
    except Exception as e:  # pragma: no cover
        excName = e.__class__.__name__
        if excName == 'OperationalError':
            return []


def read_frame(sql, eng, index_col=None, coerce_float=True):
    """
    Returns a DataFrame corresponding to the result set of the query
    string.

    Optionally provide an index_col parameter to use one of the
    columns as the index. Otherwise will be 0 to len(results) - 1.

    Parameters
    ----------
    sql: string
        SQL query to be executed
    eng: sqlalchemy engine
    index_col: string, optional
        column name to use for the returned DataFrame object.
    """
    cur = eng.execute(sql)
    rows = _safe_fetch(cur)
    columns = cur.keys()

    cur.close()

    result = DataFrame.from_records(rows, columns=columns,
                                    coerce_float=coerce_float)

    if index_col is not None:
        result = result.set_index(index_col)

    return result

frame_query = read_frame