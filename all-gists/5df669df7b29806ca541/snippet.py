# -*- coding: utf-8 -*-
import pandas
from pymaps import Map, PyMap, Icon

# import data
data = pandas.read_csv('data.csv', index_col=0)

# prepare map
tmap = Map()
tmap.zoom = 2

# prepare icons
iconRed = Icon('iconRed')
iconRed.image = "http://labs.google.com/ridefinder/images/mm_20_red.png"
iconRed.shadow = "http://labs.google.com/ridefinder/images/mm_20_shadow.png"
iconBlue = Icon('iconBlue')
iconBlue.image = "http://labs.google.com/ridefinder/images/mm_20_blue.png"
iconBlue.shadow = "http://labs.google.com/ridefinder/images/mm_20_shadow.png"
iconGreen = Icon('iconGreen')
iconGreen.image = "http://labs.google.com/ridefinder/images/mm_20_green.png"
iconGreen.shadow = "http://labs.google.com/ridefinder/images/mm_20_shadow.png"
iconYellow = Icon('iconYellow')
iconYellow.image = "http://labs.google.com/ridefinder/images/mm_20_yellow.png"
iconYellow.shadow = "http://labs.google.com/ridefinder/images/mm_20_shadow.png"

# create points
for x, row in data.T.iteritems():
    icon = iconRed.id
    point = (row['Lat'], row['Long'], text, icon)
    tmap.setpoint(point)


# create googlemap
gmap = PyMap(key='XXXXXXXXXXXXXXXXXX', maplist=[tmap])
gmap.addicon(iconGreen)
gmap.addicon(iconYellow)
gmap.addicon(iconBlue)
gmap.addicon(iconRed)

# output
open('Data.html','wb').write(gmap.showhtml())