from pyspark.sql.functions import udf
from pyspark.sql.types import BooleanType

def regex_filter(x):
    regexs = ['.*ALLYOURBASEBELONGTOUS.*']
    
    if x and x.strip():
        for r in regexs:
            if re.match(r, x, re.IGNORECASE):
                return True
    
    return False 
    
    
filter_udf = udf(regex_filter, BooleanType())

df_filtered = df.filter(filter_udf(df.field_to_filter_on))