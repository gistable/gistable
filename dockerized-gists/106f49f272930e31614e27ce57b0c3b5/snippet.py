
"""
Extracting various figures from Statnett

"""

import requests
import datetime
import pprint


_uri = "http://driftsdata.statnett.no/restapi/\
ProductionConsumption/GetLatestDetailedOverview"

_response = requests.get(_uri)
_data = dict(_response.json())

_timestamp = datetime.datetime.fromtimestamp(int(_data["MeasuredAt"])/1000.0)

datakeys = {
    'thermal': 'ThermalData',
    'unspecified': 'NotSpecifiedData',
    'consumption': 'ConsumptionData',
    'wind': 'WindData',
    'hydro':'HydroData',
    'nuclear': 'NuclearData',
    'netexchange': 'NetExchangeData',
    'prodcution': 'ProductionData'
}

def parse_value(value):
    """ parses a value """
    value = value.replace(u'-', '').replace(u'\xa0', '')
    if not value:
        return 0
    else:
        return int(value)

def load_snapshop():
    """ loading all data """

    snapshot = {"timestamp": _timestamp}


    for key in datakeys:
        details = {}
        items = _data[datakeys[key]]
        for item in items:
            area = item["titleTranslationId"]
            if area and "Total" in area:
                details[u'total'] = parse_value(item["value"])
            elif area:
                details[area[-6:-4]] = parse_value(item["value"])
        snapshot[key] = details
    return snapshot

if __name__ == "__main__":
    snapshot = load_snapshop()
    pprint.pprint(snapshot)