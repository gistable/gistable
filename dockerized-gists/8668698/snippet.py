from pyelasticsearch import ElasticSearch
import pandas as pd
from time import time

root_path="/home/clemsos/Dev/mitras/"
raw_data_path=root_path+"data/"
csv_filename="week10.csv"

t0=time()

# size of the bulk
chunksize=5000

# open csv file
f = open(raw_data_path+csv_filename) # read csv

# parse csv with pandas
csvfile=pd.read_csv(f, iterator=True, chunksize=chunksize) 

# init ElasticSearch
es = ElasticSearch('http://localhost:9200/')

# init index
try :
    es.delete_index("weiboscope")
except :
    pass

es.create_index("weiboscope")

# start bulk indexing 
print "now indexing %s..."%(csv_filename)

for i,df in enumerate(csvfile): 
    print i
    records=df.where(pd.notnull(df), None).T.to_dict()
    list_records=[records[it] for it in records]
    try :
        es.bulk_index("weiboscope","tweet",list_records)
    except :
        print "error!, skiping some tweets sorry"
        pass

print "done in %.3fs"%(time()-t0)