#!/usr/bin/env python

import os
import sys
import subprocess

#-----------------------------------------------------------------------------
def main():
    fileNames = sys.argv[1:]

    errorMessages = []
    for fileName in fileNames:
        if not isArchive(fileName):
            errorMessages.append("file is not an archive:        %s" % fileName)
        
        contentsDir = getExpandedDirName(fileName)
        if os.path.exists(contentsDir):
            errorMessages.append("directory needs to be removed: %s" % contentsDir)
            
    if len(errorMessages) > 0:
        for errorMessage in errorMessages:
            print errorMessage
        sys.exit()
            
    for fileName in fileNames:
        unzip(fileName)

#-----------------------------------------------------------------------------
def unzip(fileName):
    oDir = getExpandedDirName(fileName)
    
    os.makedirs(oDir)
    
    print "Processing: %s into: %s" % (fileName, oDir)
    
    command = "unzip %s -d %s" % (fileName, oDir)
    process = subprocess.Popen(command, shell=True)
    status  = os.waitpid(process.pid, 0)[1]
    
    walkFiles(oDir)
    
#-----------------------------------------------------------------------------
def walkFiles(dirName):
    print "walking the files of %s" % dirName
    
    dirs = os.walk(dirName)
    
    for (dirPath, dirNames, fileNames) in dirs:
        for fileName in fileNames:
            if isArchive(fileName):
                unzip(os.path.join(dirPath, fileName))

#-----------------------------------------------------------------------------
def getExpandedDirName(fileName):
    fileDir  = os.path.dirname(fileName)
    baseName = "%s.contents" % os.path.basename(fileName)
    
    return os.path.join(fileDir, baseName)

#-----------------------------------------------------------------------------
def isArchive(fileName):
    ext = fileName[-4:]
    
    if ext in [".zip", ".jar"]: return True
    return False
    
#-----------------------------------------------------------------------------
main()
