
import time
import urllib2
import json
from cartodb import CartoDBAPIKey, CartoDBException
from secret import API_KEY

URL = 'http://services.redbullstratos.com/LiveData/Get'

cl = CartoDBAPIKey(API_KEY, 'javi')

#create_table();
positions = {}
while True:
    try:
        data = json.loads(urllib2.urlopen(URL).read())
        telemetry = data['Telemetry']
        if telemetry:
            telemetry.sort(lambda x, y: x['Id'] - y['Id'])
            for t in telemetry:
                if t['Id'] not in positions:
                    positions[t['Id']] = t
                    t['the_geom'] = "ST_GeomFromText('POINT(%s %s)', 4326)" % (t['Longitude'], t['Latitude'])
                    del t['Latitude']
                    del t['Longitude']
                    del t['CompassDirection']
                    cl.sql("insert into stratos (%s) values (%s)" % (
                        ','.join(map(str, t.keys())), 
                        ','.join(map(str, t.values()))
                        )
                    )
    except Exception,e:
        print e
        pass
    time.sleep(3)
