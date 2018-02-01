# Run in QGIS python console for read-only view of CartoDB table
# Substitute your user name and query on first two lines
cartoName = ""  # PUT YOUR USER NAME IN THE QUOTES
cartoQuery = "" # PUT YOUR QUERY IN THE QUOTES

import urllib

cartoUrl = 'http://{}.cartodb.com/api/v2/sql?format=GeoJSON&q={}'.format(cartoName, cartoQuery)
response = urllib.urlopen(cartoUrl)
content = response.read()
layer = QgsVectorLayer(content, cartoName, 'ogr')
QgsMapLayerRegistry.instance().addMapLayer(layer)
