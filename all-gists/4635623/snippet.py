#
# Usage example:
# python path/to/image_tiler.py path/to/huge/image.png 256x256 3
#

import glob
import os
import re
import sys
import subprocess

#Initialization
image_file = sys.argv[1]
tile_resolution = sys.argv[2]
image_name = os.path.basename(image_file)[:-4]
image_dir = os.path.dirname(image_file)
image_ext = image_file[-3:]
num_levels = int(sys.argv[3])
output_dir = sys.argv[4] if len(sys.argv) >= 5 else "{0}/{1}_tiles".format(image_dir,
                                                                           image_name)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

#Thumbnail generation
       
#ImageMagick command to generate the thumbnail from a (possibly large) image
imagemagick_thumbnail_command = "convert {0} -thumbnail 150x150 {1}/{2}_thumb.{3}".format(image_file,
                                                                                          output_dir,
                                                                                          image_name,
                                                                                          image_ext).split()
subprocess.call(imagemagick_thumbnail_command)

print "ImageMagick thumbnail generation done."

#Image scaling and tiling

scaled_image_file = "{0}/{1}_100.{2}".format(image_dir, image_name, image_ext)
scaled_image_name = os.path.basename(scaled_image_file)[:-4]
os.rename(image_file, scaled_image_file)
image_file = scaled_image_file

for level in xrange(num_levels):
    scaling_percentage = 100/(2**level)
    
    print "Level #{0} - scaling percentage: {1}%...".format(level+1, scaling_percentage)
    
    if level > 0:
        #Scaling
        scaled_image_file = "{0}/{1}_{2}.{3}".format(image_dir, image_name,
                                                     scaling_percentage,
                                                     image_ext)
        scaled_image_name = os.path.basename(scaled_image_file)[:-4]
        
        #ImageMagick command to resize an image
        imagemagick_resize_command = "convert {0} -resize {1}% {2}".format(image_file,
                                                                           scaling_percentage,
                                                                           scaled_image_file).split()
        subprocess.call(imagemagick_resize_command)
        
    #Tiling
        
    #ImageMagick command to get image resolution
    imagemagick_identify_command = "identify -format \"%[fx:w]x%[fx:h]\" {0}".format(scaled_image_file).split()
    out = subprocess.check_output(imagemagick_identify_command)
    image_resolution = out.strip(" \"\n")

    #ImageMagick command to crop an image into tiles
    imagemagick_crop_command = "convert {0} -verbose -crop {1} {2}/%04d.{3}".format(scaled_image_file,
                                                                                    tile_resolution,
                                                                                    output_dir,
                                                                                    image_ext).split()
    out, err = subprocess.Popen(imagemagick_crop_command, stderr=subprocess.PIPE).communicate()

    print "ImageMagick crop done."
    
    #Renaming tiles
    
    image_res_array = image_resolution.split("x")
    image_x_res = int(image_res_array[0])
    image_y_res = int(image_res_array[1])
    tile_res_array = tile_resolution.split("x")
    tile_x_res = int(tile_res_array[0])
    tile_y_res = int(tile_res_array[1])

    num_columns = image_x_res / tile_x_res + (0 if image_x_res % tile_x_res == 0 else 1)

    for tile_file in re.findall("=>(.*)\[", err):
        number = int(os.path.basename(tile_file)[:-4])
        row = number / num_columns
        column = number % num_columns
        new_name = "{0}/{1}_{2}_{3}.{4}".format(output_dir, scaled_image_name,
                                                column, row, image_ext)
        try:
            os.rename(tile_file, new_name)
        except OSError as e:
            print e    

    print "Tiles renaming done."
    
    print "Level #{0} complete.".format(level+1)

#Finalization

os.rename(image_file, "{0}/{1}.{2}".format(image_dir, image_name, image_ext))