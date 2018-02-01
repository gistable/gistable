import arcpy
import os

def create_path(path):
    if not os.path.exists(path):
        print "Creating directory {}".format(path)
        os.makedirs(path)


# default application data dir; e.g. c:\Users\scw\AppData\Roaming
app_data_path = os.getenv('APPDATA')

# get current ArcGIS version
arc_version = arcpy.GetInstallInfo()['Version']

# change this path if you'd like the spatial references to be written 
# out elsewhere, this is the default directory for .prj files.
output_base = '{0}\\ESRI\\Desktop{1}\\ArcMap\\Coordinate Systems'.format(app_data_path, arc_version)
create_path(output_base)

for sr_name in arcpy.ListSpatialReferences():
    # spatial reference names use a single \ separator, double them up.
    sr_filename = "{}.prj".format(sr_name.replace("/", "\\"))
    output_file = os.path.join(output_base, sr_filename)
    output_dir = os.path.dirname(output_file)

    # create this parent directory, if needed
    create_path(output_dir)

    with open(output_file, 'w') as prj_file:
        sr = arcpy.SpatialReference(sr_name)
        prj_file.write(sr.exportToString())