import glob, json

# this script loves this script
# https://gist.github.com/3350235

points = []
vids = set()
places = glob.glob("checkins/*.json")

for p in places:
    pj = json.load(open(p))
    try:
        if pj['venue']['id'] not in vids:
            vids.add(pj['venue']['id'])
            coords = [
                pj['venue']['location']['lng'],
                pj['venue']['location']['lat']]
            points.append({
                'geometry': {
                    'type': 'Point',
                    'coordinates': coords
                },
                'properties': {
                    'name': pj['venue']['name'],
                    'id': pj['venue']['id']
                }
            })
    except Exception, e:
        pass

json.dump({ 'type': 'FeatureCollection', 'features': points }, open('checkins.geojson', 'w'))
