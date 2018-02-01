#!/usr/bin/env python
#
# This is example usage for using ilmatieteelaitos api for a fetching
# temperature forecast for a certain LAT & LON position for next 8 hours.
# https://ilmatieteenlaitos.fi/avoin-data
#
# Licensend under MIT
#

import urllib3
from urllib3 import ProxyManager
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

# Configuration
FMI_APIKEY          = "GET-YOUR-OWN-API-KEY"
LOCATION_LAT_LON    = "61.520694,23.669950"
TIMESTEP_IN_MINUTES = "60"

endtime = datetime.now() + timedelta(hours=8)
endtime = endtime.replace(microsecond=0).isoformat()

url = "http://data.fmi.fi/fmi-apikey/%s/wfs" %(FMI_APIKEY, ) + \
        "?request=getFeature" + \
        "&storedquery_id=fmi::forecast::hirlam::surface::point::simple" + \
        "&latlon=%s" %(LOCATION_LAT_LON, ) + \
        "&endtime=%s" %(endtime, ) + \
        "&timestep=%s" %(TIMESTEP_IN_MINUTES, ) + \
        "&parameters=temperature"

http = urllib3.PoolManager()
r = http.request('GET', url)

if r.status == 200:
    root = ET.fromstring(r.data)
    for items in root.findall('.//{http://xml.fmi.fi/schema/wfs/2.0}BsWfsElement'):
        print(items[1].text + ', ' + items[3].text)
else:
    print("ERROR: something wrong\n")
    print(r.data)

# Example output
# 2016-12-28T14:00:00Z, -5.69
# 2016-12-28T15:00:00Z, -6.48
# 2016-12-28T16:00:00Z, -7.03
# 2016-12-28T17:00:00Z, -8.03
# 2016-12-28T18:00:00Z, -8.75
# 2016-12-28T19:00:00Z, -8.4
# 2016-12-28T20:00:00Z, -8.14
# 2016-12-28T21:00:00Z, -7.64
# 2016-12-28T22:00:00Z, -6.89
# 2016-12-28T23:00:00Z, -5.73

# Other possible parameters
#'ParameterName', 'GeopHeight'
#'ParameterValue', '115.68'
#'ParameterName', 'Temperature'
#'ParameterValue', '1.43'
#'ParameterName', 'Pressure'
#'ParameterValue', '1017.76'
#'ParameterName', 'Humidity'
#'ParameterValue', '94.53'
#'ParameterName', 'WindDirection'
#'ParameterValue', '241.0'
#'ParameterName', 'WindSpeedMS'
#'ParameterValue', '2.77'
#'ParameterName', 'WindUMS'
#'ParameterValue', '1.82'
#'ParameterName', 'WindVMS'
#'ParameterValue', '2.08'
#'ParameterName', 'MaximumWind'
#'ParameterValue', '2.85'
#'ParameterName', 'WindGust'
#'ParameterValue', '5.87'
#'ParameterName', 'DewPoint'
#'ParameterValue', '0.35'
#'ParameterName', 'TotalCloudCover'
#'ParameterValue', '95.5'
#'ParameterName', 'WeatherSymbol3'
#'ParameterValue', '3.0'
#'ParameterName', 'LowCloudCover'
#'ParameterValue', '95.5'
#'ParameterName', 'MediumCloudCover'
#'ParameterValue', '17.1'
#'ParameterName', 'HighCloudCover'
#'ParameterValue', '10.0'
#'ParameterName', 'Precipitation1h'
#'ParameterValue', '0.0'
#'ParameterName', 'PrecipitationAmount'
#'ParameterValue', '0.1'
#'ParameterName', 'RadiationGlobalAccumulation'
#'ParameterValue', '164747.8'
#'ParameterName', 'RadiationLWAccumulation'
#'ParameterValue', '14560511.0'
#'ParameterName', 'RadiationNetSurfaceLWAccumulation'
#'ParameterValue', '-513144.44'
#'ParameterName', 'RadiationNetSurfaceSWAccumulation'
#'ParameterValue', '95499.79'
#'ParameterName', 'RadiationDiffuseAccumulation'
#'ParameterValue', '163327.63'
