#-*- coding: iso-8859-1 -*-

import sys
import os
import requests
from sets import Set

'''
This script downloads all images found under a given path 
and with the naming schema containing a word, a trailing number and a file extension
like 'someName-000.jpg' or 'anotherName00000.png'
'''

def main():
  # first the script asks for the url of an image in the collection
  firstImageURL = raw_input('Please enter URL of the first image: ')
  # call for doing something with the URL
  fileInfo = getFileInfo(firstImageURL)

  # script asks for an folder for downloading the files to within the download directory
  # this is OSX dependent, please change this for your needs, especially the [USERNAME]
  downloadDirectory = os.path.join('/Users/[USERNAME]/Downloads', raw_input('Name a new folder for the download: '))
  # creates the demanded directory 
  if not os.path.exists(downloadDirectory):
    os.makedirs(downloadDirectory)
  # call for download
  getDownload(fileInfo, downloadDirectory)

  print('READY')
  return 0

def getFileInfo(firstImageURL):
  # splitting up the given URL to get all the information we need
  urlDirectories = firstImageURL.split('/')
  # the last part is the name of the file
  givenFileName = urlDirectories[-1]

  fileNamePieces = givenFileName.split('.')
  directoryURL = firstImageURL.replace(givenFileName, '')
  originalName = getOriginalName(fileNamePieces[0])

  # an dictionary keeps all the info and let us get the values by keys
  fileInfo = {'name': originalName[0], 'digits': originalName[1], 'extension': fileNamePieces[-1], 'path': directoryURL}

  return fileInfo

def getOriginalName(someName):
  # creating an number set for checking if the last characters are numbers
  numberSet = Set(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
  digits = 1
  # checking from behind
  while digits <= len(someName) and someName[-digits] in numberSet:
    digits += 1  
  # we must reduce the digits
  digits -= 1

  # making a list for returning just one object
  if digits == len(someName):
    name = ['', digits]

  elif digits < len(someName):
    name = [someName[:-digits], digits]
  
  return name

# this function downloads the files using the request library
def getDownload(fileInfo, downloadDirectory):
  fileNumber = 0
  # sometimes files aren’t numbered correctly, that’s why we have a error counter
  errorCount = 0
  errorMax = 10

  while errorCount < errorMax:
    # generating the file name. really like the zfill() function
    fileName = fileInfo['name'] + str(fileNumber).zfill(fileInfo['digits']) + '.' + fileInfo['extension']
    fileNumber += 1

    try:
      r = requests.get(fileInfo['path'] + fileName)

      # only download when you’ll get the right status
      if r.status_code == 200:
        # create a path where you want to save the file
        downloadPath = os.path.join(downloadDirectory, fileName)
        # create a new file write only
        downloadFile = open(downloadPath, 'w')
        # wrinting the content
        downloadFile.write(r.content)
        # always close a file
        downloadFile.close()

        print('Downloaded file: ' + fileName)

        # resetting the error counter 
        errorCount = 0

      else:
        errorCount += 1
        print 'Error No:', errorCount
        print('ERROR while downloading file: ' + fileName)

    except Exception, e:
      errorCount += 1
      print 'Error No:', errorCount
      print 'Error: ', e

if __name__ == '__main__':
  main()