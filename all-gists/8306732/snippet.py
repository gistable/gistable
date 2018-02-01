import cStringIO
import requests
from xml.etree import cElementTree as ElementTree

url = 'http://climate.weather.gc.ca/climateData/bulkdata_e.html'
query = {
    # Spelling of keys is case-sensitive at the URL-processor end
    'timeframe': 1,
    'stationID': 6831,  # Sandheads
    'format': 'xml',
    'Year': 2002,
    'Month': 9,
    'Day': 1,  # Day must be 1. Response will contain a month of data
}
response = requests.get(url, params=query)
tree = ElementTree.parse(cStringIO.StringIO(response.content))
root = tree.getroot()
raw_data = root.findall('stationdata')
for record in raw_data:
    # A real application would obviously accumulate the values from each record
    # in some kind of data structure, but we'll ignore that here

    # Date/time constituents are attributes of the stationdata element
    year = int(record.get('year'))
    month = int(record.get('month'))
    # ...etc.
    # Weather observation values are text of child elements
    wind_speed = float(record.find('windspd').text)
    wind_dir = float(record.find('winddir').text) * 10  # Observation value is in 10s of degrees
    # ...etc.