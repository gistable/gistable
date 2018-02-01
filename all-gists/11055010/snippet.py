#!/usr/bin/env python

# assuming a csv file with a name in column 0 and the image url in column 1

import urllib

filename = "images"

# open file to read
with open("{0}.csv".format(filename), 'r') as csvfile:
    # iterate on all lines
    i = 0
    for line in csvfile:
        splitted_line = line.split(',')
        # check if we have an image URL
        if splitted_line[1] != '' and splitted_line[1] != "\n":
            urllib.urlretrieve(splitted_line[1], "img_" + str(i) + ".png")
            print "Image saved for {0}".format(splitted_line[0])
            i += 1
        else:
            print "No result for {0}".format(splitted_line[0])