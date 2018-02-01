#!/usr/bin/env python
__author__ = 'kersten.clauss'
__date__ = '28.03.2015'


"""script to create a vector/polygon from Hansens 30m global tree cover dataset
(http://earthenginepartners.appspot.com/science-2013-global-forest/download_v1.1.html)

Each tile will be downloaded, filtered to >75% tree cover for 2013 and merged into a global vector datset. The format of
the vector dataset is SpatiaLite/SQLite. It is advised to use the resampling to 250m option otherwise the resulting
vector database will be quite large. With a 250m resolution it still comes in at around 5Gb.

The downloaded files will be in a subfolder called 'tmp' and removed after creation of the vector dataset if you set the
option to do so.

Requires the GDAL >=1.10.0 executables to be present.
"""

import os
import sys
import urllib

#global options
remove_original = False  # remove or keep the downloaded raster data
resample_to_250m = True  # resample to 0.0025 by 0.0025 degrees pixel size
remove_resample = False  # remove or keep the resampled raster data

if len(sys.argv) < 1:  # check if directory is given
        raise Exception("Missing directory. Usage: python tree_cover_vector.py /tree_cover/directory")
dst_dir = sys.argv[1]
tmp_dir = os.path.join(dst_dir, "tmp")

if not os.path.exists(dst_dir):  # create the output directory if it does not exist
        os.makedirs(dst_dir)
if not os.path.exists(tmp_dir):  # create the output directory if it does not exist
        os.makedirs(tmp_dir)

#lists used for the tile naming convention
longitude = ["180W", "170W", "160W", "150W", "140W", "130W", "120W", "110W", "100W",
       "090W", "080W", "070W", "060W", "050W", "040W", "030W", "020W", "010W",
       "000E", "010E", "020E", "030E", "040E", "050E", "060E", "070E", "080E", "090E",
       "100E", "110E", "120E", "130E", "140E", "150E", "160E", "170E"]

latitude = ["80N", "70N", "60N", "50N", "40N", "30N", "20N", "10N", "00N",
       "10S", "20S", "30S", "40S", "50S"]

base_url = "http://commondatastorage.googleapis.com/earthenginepartners-hansen/GFC2014/Hansen_GFC2014"

# download, calculate tree cover+gain-loss, warp to 250mx250m at equator, polygonize and append to SpatiaLite DB
for lon in longitude:
    for lat in latitude:
        print "Downloading files for lat:", lat, "lon:", lon

        tree_url = base_url+"_treecover2000_"+lat+"_"+lon+".tif"
        tree_name = "treecover2000_"+lat+"_"+lon+".tif"
        if not os.path.exists(os.path.join(tmp_dir, tree_name)):
            urllib.urlretrieve(tree_url, os.path.join(tmp_dir, tree_name))

        gain_url = base_url+"_gain_"+lat+"_"+lon+".tif"
        gain_name = "gain_"+lat+"_"+lon+".tif"
        if not os.path.exists(os.path.join(tmp_dir, gain_name)):
            urllib.urlretrieve(gain_url, os.path.join(tmp_dir, gain_name))

        loss_url = base_url+"_loss_"+lat+"_"+lon+".tif"
        loss_name = "loss_"+lat+"_"+lon+".tif"
        if not os.path.exists(os.path.join(tmp_dir, loss_name)):
            urllib.urlretrieve(loss_url, os.path.join(tmp_dir, loss_name))

        tree_name = "treecover2000_"+lat+"_"+lon+".tif"
        tree_file = os.path.join(tmp_dir, tree_name)
        gain_name = "gain_"+lat+"_"+lon+".tif"
        gain_file = os.path.join(tmp_dir, gain_name)
        loss_name = "loss_"+lat+"_"+lon+".tif"
        loss_file = os.path.join(tmp_dir, loss_name)
        out_name = "tree_cover_over75_with_gain_and_loss_"+lat+"_"+lon+".tif"
        out_file = os.path.join(tmp_dir, out_name)
        res_name = "tree_cover_over75_resampled250m_"+lat+"_"+lon+".tif"
        res_file = os.path.join(tmp_dir, res_name)

        print "Creating mask for lat:", lat, "lon:", lon
        #create binary mask for >75% tree cover, add gains, substract losses from 2000-2013
        calc_cmd = "gdal_calc.py -A \""+tree_file+"\" -B \""+gain_file+"\" -C \""+loss_file+"\" --outfile=\""+out_file+"\" --NoDataValue=0 --calc=\"1*((1*(A>75)+B-C)>0)\""
        os.system(calc_cmd)

        if resample_to_250m:
        # resample to 0.00225 by 0.00225 degrees if option is given, otherwise keep original resolution
            print "Resampling lat:", lat, "lon:", lon
            #resample to 250mx250m at equator, keep SRS, remove original resolution calc afterwards
            resample_cmd = "gdalwarp -tr 0.00225 0.00225 -r mode "+out_file+" "+res_file
            os.system(resample_cmd)og
            os.remove(out_file)
        else:  # keep original resolution
            res_file = out_file

        print "Polygonizing lat:", lat, "lon:", lon
        #polygonize
        #use -mask option to ignore no-tree-areas -> a LOT faster and smaller filesize
        polygon_name = "tree_cover_"+lat+"_"+lon+".sqlite"
        polygon_file = os.path.join(tmp_dir, polygon_name)
        polygonize_cmd = "gdal_polygonize.py -mask "+res_file+" "+res_file+" -f SQLite "+polygon_file
        os.system(polygonize_cmd)


        #append to final database
        final_name = "tree_cover_global.sqlite"
        final_file = os.path.join(dst_dir, final_name)
        if not os.path.exists(final_file):
            ogr_command = "ogr2ogr -append -f SQLite -dsco SPATIALITE=YES "+final_file+" "+polygon_file+" -nln tree_cover"
        else:
            ogr_command = "ogr2ogr -append -update -f SQLite -dsco SPATIALITE=YES "+final_file+" "+polygon_file+" -nln tree_cover"
        os.system(ogr_command)

        #remove temporary files
        os.remove(polygon_file)

        if remove_original:
            os.remove(tree_file)
            os.remove(gain_file)
            os.remove(loss_file)
        if remove_resample:
            if os.path.exists(res_file):  # necessary to catch error if original resolution is kept
                os.remove(res_file)