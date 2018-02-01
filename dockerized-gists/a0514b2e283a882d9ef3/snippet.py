##########################################################################
#
#  xmldiff
#
#    Simple utility script to enable a diff of two XML files in a way 
#     that ignores the order or attributes and elements.
#
#    Dale Lane (email@dalelane.co.uk)
#     6 Oct 2014
#
##########################################################################
#
#  Overview
#    The approach is to sort both files by attribute and element, and 
#     then reuse an existing diff implementation on the sorted files.
#
#  Arguments
#    <diffcommand> the command that should be run to diff the sorted files
#    <filename1>   the first XML file to diff
#    <filename2>   the second XML file to diff
#
#  Background
#    http://dalelane.co.uk/blog/?p=3225
#
##########################################################################

import os, sys, subprocess, platform
import lxml.etree as le
from operator import attrgetter

#
# Check required arguments
if len(sys.argv) != 4:
    print ("Usage: python xmldiff.py <diffcommand> <filename1> <filename2>")
    quit()


#
# Prepares the location of the temporary file that will be created by xmldiff
def createFileObj(prefix, name):
    return { 
        "filename" : os.path.abspath(name),
        "tmpfilename" : "." + prefix + "." + os.path.basename(name)
    }


#
# Function to sort XML elements by id 
#  (where the elements have an 'id' attribute that can be cast to an int)
def sortbyid(elem):
    id = elem.get('id')
    if id:
        try:
            return int(id)
        except ValueError:
            return 0
    return 0


#
# Function to sort XML elements by their text contents
def sortbytext(elem):
    text = elem.text
    if text:
        return text
    else:
        return ''


#
# Function to sort XML attributes alphabetically by key
#  The original item is left unmodified, and it's attributes are 
#  copied to the provided sorteditem
def sortAttrs(item, sorteditem):
    attrkeys = sorted(item.keys())
    for key in attrkeys:
        sorteditem.set(key, item.get(key))


# 
# Function to sort XML elements
#  The sorted elements will be added as children of the provided newroot
#  This is a recursive function, and will be called on each of the children
#  of items.
def sortElements(items, newroot):
    # The intended sort order is to sort by XML element name
    #  If more than one element has the same name, we want to 
    #   sort by their text contents.
    #  If more than one element has the same name and they do 
    #   not contain any text contents, we want to sort by the 
    #   value of their ID attribute.
    #  If more than one element has the same name, but has 
    #   no text contents or ID attribute, their order is left
    #   unmodified.
    #
    # We do this by performing three sorts in the reverse order
    items = sorted(items, key=sortbyid)
    items = sorted(items, key=sortbytext)
    items = sorted(items, key=attrgetter('tag'))

    # Once sorted, we sort each of the items
    for item in items:
        # Create a new item to represent the sorted version 
        #  of the next item, and copy the tag name and contents
        newitem = le.Element(item.tag)
        if item.text and item.text.isspace() == False:
            newitem.text = item.text

        # Copy the attributes (sorted by key) to the new item
        sortAttrs(item, newitem)

        # Copy the children of item (sorted) to the new item
        sortElements(list(item), newitem)

        # Append this sorted item to the sorted root
        newroot.append(newitem)


# 
# Function to sort the provided XML file
#  fileobj.filename will be left untouched
#  A new sorted copy of it will be created at fileobj.tmpfilename 
def sortFile(fileobj):
    with open(fileobj['filename'], 'r') as original:
        # parse the XML file and get a pointer to the top
        xmldoc = le.parse(original)
        xmlroot = xmldoc.getroot()

        # create a new XML element that will be the top of 
        #  the sorted copy of the XML file
        newxmlroot = le.Element(xmlroot.tag)

        # create the sorted copy of the XML file
        sortAttrs(xmlroot, newxmlroot)
        sortElements(list(xmlroot), newxmlroot)

        # write the sorted XML file to the temp file
        newtree = le.ElementTree(newxmlroot)
        with open(fileobj['tmpfilename'], 'wb') as newfile:
            newtree.write(newfile, pretty_print=True)


#
# sort each of the specified files
filefrom = createFileObj("from", sys.argv[2])
sortFile(filefrom)
fileto = createFileObj("to", sys.argv[3])
sortFile(fileto)

#
# invoke the requested diff command to compare the two sorted files
if platform.system() == "Windows":
    sp = subprocess.Popen([ "cmd", "/c", sys.argv[1] + " " + filefrom['tmpfilename'] + " " + fileto['tmpfilename'] ])
    sp.communicate()
else:
    sp = subprocess.Popen([ "/bin/bash", "-i", "-c", sys.argv[1] + " " + os.path.abspath(filefrom['tmpfilename']) + " " + os.path.abspath(fileto['tmpfilename']) ])
    sp.communicate()

#
# cleanup - delete the temporary sorted files after the diff terminates
os.remove(filefrom['tmpfilename'])
os.remove(fileto['tmpfilename'])