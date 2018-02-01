#!/usr/bin/python

"""
For more information, see: https://help.ubuntu.com/community/SlideshowWallpapers

# 1: Create the following xml file to add wallpaper slideshow
  ~/.local/share/gnome-background-properties/MyFirstSlideshowCollection.xml 
  With the following content:

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE wallpapers SYSTEM "gnome-wp-list.dtd">
<wallpapers>
  <wallpaper>
    <name>My 1st Wallpapers</name>
    <filename>.local/share/backgrounds/wallpaper1/My1stSlideshow.xml</filename>
    <options>zoom</options>
    <pcolor>#2c001e</pcolor>
    <scolor>#2c001e</scolor>
    <shade_type>solid</shade_type>
  </wallpaper>
</wallpapers>


# 2: Create wallpaper slideshow definition in corresponding xml file. 
  As defined above (Or could be any filename you define):

.local/share/backgrounds/wallpaper1/My1stSlideshow.xml


# 3: Run following script, replace wallpaper picture folder and slideshow xml file with your own. 
  Replace static time and transition time with what you like


# 4: For Ubuntu, go to System Settings -> Apperance. 
  You should be able to see a new wallpaper slideshow created by your own.


# 5: Any time you update the Pictures folder, run the script again to refresh the xml file.


<del>It worked on my machine (Ubuntu 14.04).</del>

"""

import os

# Settings
HOME = os.environ["HOME"]
PIC_PATH = os.path.join (HOME, "Pictures/Wallpaper/")
CONF_PATH = os.path.join (HOME, ".local/share/backgrounds/wallpaper1/My1stSlideshow.xml")

STAT_DUR = 300.0
TRANS_DUR = 2.0

# XML STRINGS
XML = "<background>\n \
<starttime>\n \
   <year>1970</year>\n\
   <month>01</month>\n\
   <day>01</day>\n\
   <hour>00</hour>\n\
   <minute>00</minute>\n\
   <second>00</second>\n\
</starttime>\n\
{0} \n\
</background>"

STATIC = "<static>\n\
<duration>{0}</duration>\n\
<file>{1}</file>\n\
</static>"

TRANS = "<transition>\n\
<duration>{0}</duration>\n\
<from>{1}</from>\n\
<to>{2}</to>\n\
</transition>"


# func to gen TRANSITION, return transition XML
def gen_trans (pic_path):
    dir = os.listdir (pic_path)

    # tick out non-pic files
    for i in dir:
        if not any (i.endswith (s) for s in [".jpg", ".png", ".gif"]):
            dir.remove (i)

    # make list of transition definitions in xml
    trans_list = []
    for i in range (len (dir)):
        trans_list.append (STATIC.format 
                           (STAT_DUR,
                            os.path.join (pic_path, dir[i]))
                          )

        if i == len (dir) - 1:
            j = 0
        else:
            j = i + 1

        trans_list.append (TRANS.format 
                          (TRANS_DUR,
                           os.path.join (pic_path, dir[i]),
                           os.path.join (pic_path, dir[j]))
                          )

    return "\n".join (trans_list)


# main
def main ():

    trans = gen_trans (PIC_PATH)
    xml = XML.format (trans)

    f = open (CONF_PATH, 'w')
    f.write (xml)
    f.close ()


main ()
