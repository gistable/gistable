"""
tiny script to convert a pandas data frame into a JSON object
"""

import ujson as json
import pandas
import numpy as np

df = pandas.DataFrame({
    "time" : [1,2,3,4,5],
    "temp" : np.random.rand(5)
})

d = [ 
    dict([
        (colname, row[i]) 
        for i,colname in enumerate(df.columns)
    ])
    for row in df.values
]
return json.dumps(d)