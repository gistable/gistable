import string
import time
import urllib2


'''
Generate KML for London postcode regions
'''

url_base = 'http://www.free-postcode-maps.co.uk/_polygons/'

locations = ['N', 'E', 'SE', 'SW', 'W', 'NW']
nums = range(1, 30)
# postcodes included in the set: (N|S)?(W|E)?[1-2]?[0-9] e.g. N1, W10
all_postcodes = ['%s%s' % (x, y) for x in locations for y in nums]
# postcodes of the form (E|W)C[1-5][A-Z] e.g. EC4V, WC2N
all_postcodes += ['%s%s%s' % (x, y, z) for x in ['EC', 'WC'] for y in range(1, 6) for z in string.ascii_uppercase]
# postcodes included in the set: (N|S)?(W|E)?1[A-Z] e.g. SW1A, W1D
all_postcodes += ['%s1%s' % (x, y) for x in locations for y in string.ascii_uppercase]
valid_postcodes = []

# try everything that looks like a London postcode
for postcode in all_postcodes:
    try:
        # first try to load from file
        with open('%s.txt' % postcode, 'r') as in_file:
            print('Already written data for %s' % postcode)
    except IOError:
        try:
            # try to download
            data = urllib2.urlopen('%s%s.txt' % (url_base, postcode)).read()
            print('Writing data for %s' % postcode)
            with open('%s.txt' % postcode, 'w') as f:
                f.write(data)
        except urllib2.HTTPError:
            print('Couldn\'t find data for %s' % postcode)
            continue
    valid_postcodes.append(postcode)

# kml boilerplate
pre_file = '<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Folder>'
post_file = '</Folder></kml>'
pre_kml = '<Placemark><name>%s</name><Polygon><outerBoundaryIs><LinearRing><coordinates>'
post_kml = '</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>'

with open('output.kml', 'w') as out_file:
    out_file.write(pre_file)
    for postcode in valid_postcodes:
        with open('%s.txt' % postcode, 'r') as in_file:
            data = in_file.read()
        out_file.write(pre_kml % postcode)
        # coordinates need swapping
        out_file.write(',0\n'.join([','.join(coords.split(',')[::-1]) for coords in data.split('\n') if coords != '']))
        out_file.write(post_kml)
    out_file.write(post_file)

