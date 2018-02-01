import json
from pandas.io.json import json_normalize
import pandas as pd

with open('C:\filename.json') as f:
    data = json.load(f)

df = pd.DataFrame(data)   

normalized_df = json_normalize(df['nested_json_object'])

'''column is a string of the column's name.
for each value of the column's element (which might be a list),
duplicate the rest of columns at the corresponding row with the (each) value.
'''

def flattenColumn(input, column):
    column_flat = pd.DataFrame([[i, c_flattened] for i, y in input[column].apply(list).iteritems() for c_flattened in y], columns=['I', column])
    column_flat = column_flat.set_index('I')
    return input.drop(column, 1).merge(column_flat, left_index=True, right_index=True)
    
new_df = flattenColumn(normalized_df, 'column_name')