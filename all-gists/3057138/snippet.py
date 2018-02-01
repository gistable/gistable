import pyodbc
import numpy as np
import datetime
import pandas

def processCursor(cur, dataframe=False):
    datatypes = []
    colinfo = cur.description
    for col in colinfo:
        if col[1] == unicode:
            datatypes.append((col[0], 'U%d' % col[3]))
        elif col[1] == str:
            datatypes.append((col[0], 'S%d' % col[3]))
        elif col[1] == float:
            datatypes.append((col[0], 'f4'))
        elif col[1] == datetime.datetime:
            datatypes.append((col[0], 'O4'))
        elif col[1] == int:
            datatypes.append((col[0], 'i4'))

    data = []
    for row in cur:
        data.append(tuple(row))

    array = np.array(data, dtype=datatypes)
    if dataframe:
        output = pandas.DataFrame.from_records(array)
    else:
        output = array

    return output
