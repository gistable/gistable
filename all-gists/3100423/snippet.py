def rows_as_update_dicts(cursor):
    colnames = cursor.fields
    for row in cursor:
        row_object = dict(zip(colnames, row))
        yield row_object
        cursor.updateRow([row_object[colname] for colname in colnames])

with arcpy.da.UpdateCursor(r'c:\data\world.gdb\world_cities', ['CITY_NAME']) as sc:
    for row in rows_as_update_dicts(sc):
        row['CITY_NAME'] = row['CITY_NAME'].title()
        print "Updating city name to {}".format(row['CITY_NAME'])