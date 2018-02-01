import pandas as pd
import requests, json, geojson
from geojson import Feature, Point, LineString, FeatureCollection

def makeDataFrame(datalist):
    rawdata=zip(*datalist)
    return pd.DataFrame( {'from':list(rawdata[0]),'to':list(rawdata[1])} )
    
def geocode_mapquest(q,limit='1',format='json'):
    url = 'http://open.mapquestapi.com/nominatim/v1/search'

    params = dict(
        format=format,
        limit=limit,
        q=q
    )
    
    data = requests.get(url=url, params=params)
    return json.loads(data.content)
    
def getUniqueLocations(data,fr='from',to='to'):
    locations=list(set(data[fr].tolist()).union(set(data[to].tolist())))
    return locations

def geocoder(locations):
    geolocations={}
    for location in locations:
        raw=geocode_mapquest(location)[0]
        geolocations[location]={
                                'json':raw,
                                'lat':float(raw['lat']),
                                'lon':float(raw['lon']),
                                'lonlat':(float(raw['lon']),float(raw['lat']))
                                }
    return geolocations
    
def geoannotate_data(data,geodata,fr='from',to='to'):
    data['from_lonlat']=data[fr].apply(lambda x: geodata[x]['lonlat'])
    data['to_lonlat']=data[to].apply(lambda x: geodata[x]['lonlat'])
    return data
    
def geojsonify(locations, geodata, data):
    features=[]
    for location in locations:
        features.append( Feature(geometry=Point( geodata[location]['lonlat'] ), id=location) )
    for row_index, row in data.iterrows():
        features.append( Feature(geometry=LineString([ row['from_lonlat'],row['to_lonlat'] ])))
    return FeatureCollection(features)
    
def oneshot(data,fr='from',to='to'):
    locations=getUniqueLocations(data,fr,to)
    geodata=geocoder(locations)
    data=geoannotate_data(data,geodata,fr,to)
    return geojsonify(locations, geodata,data)
    
def oneshot_from_file(filename,fr='from',to='to'):
    data=pd.read_csv(filename)
    locations=getUniqueLocations(data,fr,to)
    geodata=geocoder(locations)
    data=geoannotate_data(data,geodata,fr,to)
    return geojsonify(locations, geodata,data)
    
def save_geojson(data,path):
    with open(path, 'w') as outfile:
        geojson.dump(data, outfile)

def oneshot_from_datalist(datalist):
    data=makeDataFrame(datalist)
    return oneshot(data)
    
def oneshot_from_file_to_file(filename,fr='from',to='to'):
    gjdata=oneshot_from_file(filename,fr,to)
    save_geojson(gjdata,filename.replace('.csv','.json'))