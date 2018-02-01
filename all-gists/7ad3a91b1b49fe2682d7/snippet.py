#
# @author Cindy Williams
# @date 25/06/2013
#
# Loops over an existing spreadsheet with attribute data
# and builds up a definition query to apply to the dataset.
#
# For use in the Python window in ArcMap.
#

from arcpy import da
import arcpy.mapping as MAP

# Input variables
xls = r"C:\Some\Arb\Folder\Data.xlsx\Sheet1$" # Spreadsheet
mxd = MAP.MapDocument("CURRENT") # Current map document
lyr = MAP.ListLayers(mxd)[0] # First layer in the the map
lst_qry = [] # List to hold the query
field_name = "Layer"

# Loops over the spreadsheet using a search cursor.
# Appends each value into the list
with arcpy.da.SearchCursor(xls, field_name) as cursor:
    for row in cursor:
        defn_qry = """ "{0}" = '{1}' """.format(field_name, row[0])
        lst_qry.append(defn_qry)

# Build a string representation of the definition query and apply it to the layer
lyr.definitionQuery = ' OR '.join(lst_qry)

# Refresh ArcMap to see the query applied
arcpy.RefreshActiveView()
