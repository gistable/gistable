# This is a script that I use to convert geojson to
# features in a file gdb
# Step 1. Use the REST page of an ArcGIS Map Service to
# 	get the esri json results of the data you want.
# Step 2. I used my EsriJSON to GeoJSON app to convert
#	the results to geojson. http://esritogeo.herokuapp.com/
# Step 3. In ArcMap, use the python window to create a
#	python dictionary of your geojson.
# Step4. Use the following script to convert that geojson
#	into featureclasses and then merge them.
arcpy.env.workspace = r'C:\WorkSpace\target.gdb'
# I'm going to save my features to a list for merge later
items = []
for g in geojson["features"]:
	# Refer to AsShape docs
	# http://help.arcgis.com/en/arcgisdesktop/10.0/help/000v/000v00000153000000.htm
	# AsShape only creates a geometry object, so it's up to you
	# 	to use the AddField/Calculate field tools if you want to get the
	# 	attribute data across.
	geom = arcpy.AsShape(g["geometry"])
	# Save an id I'll use to calculate my field
	my_id = str(g["properties"]["ID_FIELD"])
	feature = "_" + str(my_id)
	# refer to the Copy Features docs
	# http://help.arcgis.com/en/arcgisdesktop/10.0/help/0017/001700000035000000.htm
	arcpy.CopyFeatures_management(geom, feature)
	# refer to the AddField docs
	# http://help.arcgis.com/en/arcgisdesktop/10.0/help/0017/001700000047000000.htm
	arcpy.AddField_management(feature, "ID_FIELD", "TEXT", 12, "", "", "ID_FIELD", "NULLABLE")
	# refer to the CalculateField docs
	# http://help.arcgis.com/en/arcgisdesktop/10.0/help/0017/00170000004m000000.htm
	try:
		arcpy.CalculateField_management(feature, "ID_FIELD", '"' + my_id + '"', "PYTHON")
	except Exception, e:
		print e
		arcpy.CalculateField_management(feature, "ID_FIELD, 0, "PYTHON")
	# save my features to a list
	items.append(feature)
	del geom
	
target = "all_features"
# refer to Merge docs
# http://help.arcgis.com/en/arcgisdesktop/10.0/help/0017/001700000055000000.htm
arcpy.Merge_management(items, target)
# then loop my list and
# delete my individual features
# http://help.arcgis.com/en/arcgisdesktop/10.0/help/0017/001700000052000000.htm
# This only deleted them from my map project, not the file gdb
for i in items:
	arcpy.Delete_management(i, "")
del items

# If someone knows of a more efficient way to do this, I'd love to hear about it.
# This script isn't exactly a speed demon.