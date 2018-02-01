import yaml
import json
import pandas as pd

df = pd.DataFrame({'one': [1.0, 2.1, 3.2], 'two': [4.3, 5.4, 6.5]})

with open('df.yml', 'w') as file:
    yaml.dump({'result': json.loads(df.to_json(orient='records'))}, file, default_flow_style=False)
