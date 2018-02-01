#
# elevation: A very simple python script that get elevation from latitude and longitude with google maps API by Guillaume Meunier
# 
# -----------------------------------
# NO DEPENDANCIES except JSON and URLLIB
# -----------------------------------
# 
# Copyright (c) 2016, Guillaume Meunier <alliages@gmail.com> 
# GEOJSON_export is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# GEOJSON_export is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GEOJSON_export; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>
#
# EXAMPLE :
# print elevation(48.8445548,2.4222176)

import json
import urllib

def elevation(lat, lng):
    apikey = "USE YOUR OWN KEY !!!"
    url = "https://maps.googleapis.com/maps/api/elevation/json"
    request = urllib.urlopen(url+"?locations="+str(lat)+","+str(lng)+"&key="+apikey)
    try:
        results = json.load(request).get('results')
        if 0 < len(results):
            elevation = results[0].get('elevation')
            # ELEVATION
            return elevation
        else:
            print 'HTTP GET Request failed.'
    except ValueError, e:
        print 'JSON decode failed: '+str(request)