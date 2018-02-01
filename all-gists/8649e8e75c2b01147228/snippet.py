#!/usr/bin/python
'''
Simple sample influxdb client code
'''

from influxdb import client as influxdb
import time
import pprint

host='localhost'
port = 8086
user = "root"
password = "root"
db_name = "hello_world"
db = influxdb.InfluxDBClient(host, port, user, password)
all_dbs_list = db.get_database_list()
# that list comes back like: [{u'name': u'hello_world'}]
if db_name not in [str(x['name']) for x in all_dbs_list]:
    print "Creating db {0}".format(db_name)
    db.create_database(db_name)
else:
    print "Reusing db {0}".format(db_name)
db.switch_db(db_name)

#if time not specified, the the current time will be inserted... server-side or client-side? dunno.
#db.write_points_with_precision([{"points":[[1,1,1]], "name":"foo", "columns":["a","b","c"]}], time_precision='u')
db.write_points_with_precision([{"points":[[1400000000000,1,1,1]], "name":"foo", "columns":["time", "a","b","c"]}], time_precision='u')
db.write_points_with_precision([{"points":[[1400000010000,2,1,1]], "name":"foo", "columns":["time", "a","b","c"]}], time_precision='u')
db.write_points_with_precision([{"points":[[1400000020000,2,2,1]], "name":"foo", "columns":["time", "a","b","c"]}], time_precision='u')
db.write_points_with_precision([{"points":[[1400000030000,3,2,2]], "name":"foo", "columns":["time", "a","b","c"]}], time_precision='u')
db.write_points_with_precision([{"points":[[1400000040000,3,3,2]], "name":"foo", "columns":["time", "a","b","c"]}], time_precision='u')
db.write_points_with_precision([{"points":[[1400000050000,3,3,3]], "name":"foo", "columns":["time", "a","b","c"]}], time_precision='u')
series = db.query("list series;")
print "series: {0}".format(series)
allthe = db.query("select * from {0}".format(series[0]['name']), time_precision='u')
print "all the thing:"
pprint.pprint(allthe)
# To see pretty things log in to your influxdb UI (probably http://localhost:8083/) and run a query like `select * from foo`
