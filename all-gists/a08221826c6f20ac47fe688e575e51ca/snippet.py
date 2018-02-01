import requests
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib as mpl
from collections import OrderedDict
import math

# Example: http://i.imgur.com/IXd0IVM.png

## EDIT THESE SETTINGS ##
PLEXPY_APIKEY = 'XXXXXXXXX'  # Your PlexPy API key
PLEXPY_URL = 'http://localhost:8181/'  # Your PlexPy URL

# Replace LAN IP addresses that start with the LAN_SUBNET with a WAN IP address
# to retrieve geolocation data. Leave REPLACEMENT_WAN_IP blank for no replacement.
LAN_SUBNET = ('127.0.0')
REPLACEMENT_WAN_IP = ''

# Find your user_id number and play at least one file from the server.
# This will be used to mark the server location.
SERVER_USER_ID = ''
# Enter Friendly name for Server ie 'John Smith'
SERVER_FRIENDLY = ''

# Server location information. Find this information on your own.
# If server plot is out of scope add print(geo_lst) after ut.user_id loop ~line 151 to find the error
SERVER_LON = ''
SERVER_LAT = ''
SERVER_CITY = ''
SERVER_STATE = ''
## End of edit ##

## Map stuff ##
# Map draw size
plt.figure(figsize=(16, 8))
m = Basemap(llcrnrlon=-119, llcrnrlat=22, urcrnrlon=-54, urcrnrlat=55, projection='lcc', resolution='l', lat_1=32,
            lat_2=45, lon_0=-95)
# remove line in legend
mpl.rcParams['legend.handlelength'] = 0
# title of map
title_string = "Location of Plex users based on ISP data"

m.drawmapboundary(fill_color='#1F1F1F')
m.drawcoastlines()
m.drawstates()
m.drawcountries()
m.fillcontinents(color='#3C3C3C', lake_color='#1F1F1F')

class GeoData(object):
    def __init__(self, data=None):
        data = data or {}
        self.continent = data.get('continent', 'N/A')
        self.country = data.get('country', 'N/A')
        self.region = data.get('region', 'N/A')
        self.city = data.get('city', 'N/A')
        self.postal_code = data.get('postal_code', 'N/A')
        self.timezone = data.get('timezone', 'N/A')
        self.latitude = data.get('latitude', 'N/A')
        self.longitude = data.get('longitude', 'N/A')
        self.accuracy = data.get('accuracy', 'N/A')

class UserTB(object):
    def __init__(self, data=None):
        data = data or []
        self.user_id = [d['user_id'] for d in data]

class UserIPs(object):
    def __init__(self, data=None):
        data = data or []
        self.ip_address = [d['ip_address'] for d in data]
        self.friendly_name = [d['friendly_name'] for d in data]
        self.play_count = [d['play_count'] for d in data]

def get_get_users_tables():
    # Get the user IP list from PlexPy
    payload = {'apikey': PLEXPY_APIKEY,
               'cmd': 'get_users_table'}
               
    try:
        r = requests.get(PLEXPY_URL.rstrip('/') + '/api/v2', params=payload)
        response = r.json()
        res_data = response['response']['data']['data']
        return UserTB(data=res_data)
    
    except Exception as e:
        sys.stderr.write("PlexPy API 'get_get_users_tables' request failed: {0}.".format(e))
        
def get_get_users_ips(user_id=''): 
    # Get the user IP list from PlexPy
    payload = {'apikey': PLEXPY_APIKEY,
               'cmd': 'get_user_ips',
               'user_id': user_id,
               'length': 25} #length is number of returns, default is 25
              
    try:
        r = requests.get(PLEXPY_URL.rstrip('/') + '/api/v2', params=payload)
        response = r.json()

        res_data = response['response']['data']['data']
        return UserIPs(data=res_data)
    except Exception as e:
        sys.stderr.write("PlexPy API 'get_get_users_ips' request failed: {0}.".format(e))

def get_geoip_info(ip_address=''):
    # Get the geo IP lookup from PlexPy
    payload = {'apikey': PLEXPY_APIKEY,
               'cmd': 'get_geoip_lookup',
               'ip_address': ip_address}

    try:
        r = requests.get(PLEXPY_URL.rstrip('/') + '/api/v2', params=payload)
        response = r.json()
        if response['response']['result'] == 'success':
            data = response['response']['data']
            if data.get('error'):
                raise Exception(data['error'])
            else:
                sys.stdout.write("Successfully retrieved geolocation data.")
                return GeoData(data=data)
        else:
            raise Exception(response['response']['message'])
    except Exception as e:
        sys.stderr.write("PlexPy API 'get_geoip_lookup' request failed: {0}.".format(e))
        return GeoData()


if __name__ == '__main__':
    geo_lst = [[SERVER_LON, SERVER_LAT, SERVER_CITY, SERVER_STATE, SERVER_USER_ID, REPLACEMENT_WAN_IP, SERVER_FRIENDLY, 0]]
    ut = get_get_users_tables()
    for i in ut.user_id:
        ip = get_get_users_ips(user_id=i)
        c = 0
        if ip is not None:
            fn = [x.encode('UTF8') for x in ip.friendly_name]
            fn = list(set(fn))
            ulst = [str(i)]
            for x in ip.ip_address:
                if x.startswith(LAN_SUBNET) and REPLACEMENT_WAN_IP:
                    x = REPLACEMENT_WAN_IP

                g = get_geoip_info(ip_address=x)
                glst = [str(g.longitude)] + [str(g.latitude)] + [str(g.city)] + [str(g.region)]
                geo_lst += [glst + ulst + [str(x)] + fn + [ip.play_count[c]]]
                c += 1

    for (lon, lat, city, reg, user_id, ip, fn, pc) in geo_lst:
        if user_id == SERVER_USER_ID and ip == REPLACEMENT_WAN_IP:
            color = '#FFAC05'
            marker = '*'
            markersize = 10
        else:
            color = '#A96A1C'
            marker = '.'
            markersize = 5 + pc * .1
        x, y = m(lon, lat)
        labels = 'Location: ' + city + ', ' + reg + ' User: ' + fn
        # Keeping lines inside the USA. Plots outside USA will still be in legend
        if float(lon) != float(SERVER_LON) and float(lat) != float(SERVER_LAT) and -124.0 < float(lon) < 66.0:
            # Drawing lines from Server location to client location
            m.drawgreatcircle(float(SERVER_LON), float(SERVER_LAT), float(lon), float(lat), linewidth=1, alpha=0.4,
                              color='#AC7420')
        m.plot(x, y, marker=marker, color=color, markersize=markersize, label=labels, alpha=0.3)

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    leg = plt.legend(by_label.values(), by_label.keys(), fancybox=True, fontsize='x-small', numpoints=1, title="Legend")
    if leg:
        lleng = len(leg.legendHandles)
        for i in range(0, lleng):
            leg.legendHandles[i]._legmarker.set_markersize(5)
            leg.legendHandles[i]._legmarker.set_alpha(1)
        leg.get_title().set_color('#7B777C')
        leg.draggable()
        leg.get_frame().set_facecolor('#2C2C2C')
        for text in leg.get_texts():
            plt.setp(text, color='#A5A5A7')

    plt.title(title_string)
    plt.show()
            