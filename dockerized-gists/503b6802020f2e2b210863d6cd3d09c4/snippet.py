import lxml
import urllib
import requests
import tabulate
import pandas as pd



# don't ask my why this is distributed via CSV only, not via REST API
csv_params = {
    'sep': ';'
}
wl_haltestellen = pd.read_csv('wienerlinien-ogd-haltestellen.csv', **csv_params)
wl_linien = pd.read_csv('wienerlinien-ogd-linien.csv', **csv_params)
wl_steige = pd.read_csv('wienerlinien-ogd-steige.csv', **csv_params)


address = "Lehargasse 6-8"


URI = "http://www.wienerlinien.at/ogd_routing/XML_TRIP_REQUEST2"
params = {
    'locationServerActive': 1,
    'sessionID': 0,
    'type_origin': 'any',
    'name_origin': address
}


def find_haltestellen_id(stopid):
    r = wl_haltestellen[wl_haltestellen['DIVA'] == int(stopid)]['HALTESTELLEN_ID'].values
    if len(r) != 1:
        raise ValueError("Unexpected number of haltestellen_ids for stopid={} found {}".format(stopid, len(r)))
    return r[0]

def find_rbl(stopid):
    haltestellen_id = find_haltestellen_id(stopid)
    return list(wl_steige[wl_steige['FK_HALTESTELLEN_ID'] == haltestellen_id]['RBL_NUMMER'].values.astype(int))


r = requests.get(URI, params=params)
root = lxml.etree.fromstring(r.content)


root.findall('itdTripRequest/itdOdv/itdOdvName')

#odvNameElem
#odvNameInput

root.attrib['lengthUnit']

stops_xml = root.findall('itdTripRequest/itdOdv/itdOdvAssignedStops/itdOdvAssignedStop')
# seems to be sorted by distance already
stops = [{
        'stopID': stop_xml.attrib['stopID'],
        'RBLs': find_rbl(stop_xml.attrib['stopID']),
        'name': stop_xml.text,
        'distanceTime': stop_xml.attrib['distanceTime'],
        'distance': stop_xml.attrib['distance']
    }
    for stop_xml in stops_xml
]

rbls = [rbl for stop in stops for rbl in stop['RBLs']]


stop_table = tabulate.tabulate(stops, headers='keys')
print(stop_table)

print(rbls)