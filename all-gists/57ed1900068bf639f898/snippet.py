'''
This program is free software. 
It comes without any warranty, to the extent permitted by applicable law. 
You can redistribute it and/or modify it under the terms of the WTFPL Version 2, as published by Sam Hocevar.
See wikipedia.org/wiki/WTFPL for more details.

Created on 2014-25-11

@author: Aries McRae
'''

import os, csv

folder1 = './folder1/'
folder2 = './folder2/'


def getFilename(folder, prefix):
    filename = ''
    
    for file in os.listdir(folder):
        if file.startswith(prefix):
            filename = folder + file
            break
        #if
    #for 
    
    return filename
#def



folderDict = {}

csvReader = csv.reader( open('./files.properties'))



for row in csvReader:
    for value in row:
        folder1Filename = getFilename(folder1, value)
        folder2Filename = getFilename(folder2, value)
        
        folderDict[folder1Filename] = folder2Filename
    #for
#for



def compare(filename1, filename2):
    for row in open(filename1).readlines():
        if row not in open(filename2).read():
            writeToFile(row + ' not in ' + filename2)
        #
    #for
#def



def writeToFile(data) :
    with open('./error.txt', 'a') as output:
        output.write(data + '\n')
    #endWith
#endDef 



for key, value in folderDict.items():
    compare(key, value)
#
