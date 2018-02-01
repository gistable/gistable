import csv
import simplegeo

OAUTH_TOKEN = '[insert_oauth_token_here]'
OAUTH_SECRET = '[insert_oauth_secret_here]'
CSV_FILE = '[insert_csv_file_here]'
LAYER = '[insert_layer_name_here]'

client = simplegeo.Client(OAUTH_TOKEN, OAUTH_SECRET)


def insert(data):
    layer = LAYER
    id=data.pop("id")
    lat=data.pop("latitude")
    lon=data.pop("longitude")
    # Grab more columns if you wish
    record = simplegeo.Record(layer,id,lat,lon,**data)
    client.add_record(record)

r = csv.DictReader(open(CSV_FILE, mode='U'))
for l in r:
    insert(l)