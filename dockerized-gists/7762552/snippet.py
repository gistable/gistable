"""
A script for downloading some podcasts and tagging the files so I can import them to iTunes.
"""

import pycurl
import os.path
import sys

from BeautifulSoup import BeautifulStoneSoup
import eyed3
from eyed3.mp3 import isMp3File


OUTPUT_DIRECTORY = "./"


def generateFilename(title, url):
    url = url.split('.')
    title = title.replace(' ','_')
    return "%s.%s" % ( title, url[-1])


def generateFilepath(filename):
    return OUTPUT_DIRECTORY + filename


def fetchContent(output_filepath, url):
    '''
    Download and save the content
    '''

    #Don't re-download
    if os.path.exists(output_filepath):
        return True

    #Downloads are slow. Give a status.
    print "Fetching", url

    destination = None
    try:
        destination = open(output_filepath, 'w')
        remote_file_location = pycurl.Curl()
        remote_file_location.setopt(remote_file_location.URL, url)
        remote_file_location.setopt(remote_file_location.WRITEFUNCTION, destination.write)
        remote_file_location.perform()
    except IOError as ex:
        print "IO error saving ", url, ":", ex
        destination.close()
        os.remove(output_filepath)
        return False
    except Exception as ex:
        print "Error: ", ex, " did not fetch ", output_filepath
        destination.close()
        os.remove(output_filepath)
        return False

    destination.close()
    print "... done."
    
    return True


def addTags(filepath, title, author, album, ):
    '''
    Set info tags on MP3 so iTunes will search and sort
    '''

    mp3 = None
    try:
        #Ran into some NotImplemented errors on this step
        #so gave it its own special try block.
        if not eyed3.mp3.isMp3File(filepath):
            return

        mp3 = eyed3.load(filepath)
    except NotImplementedError as ex:
        print "Couldn't open file  %s to add tag, error was %s " % ( filepath, ex )
        return

    try:
        if not mp3.tag:
            mp3.initTag()
        tag = mp3.tag
        tag.artist = unicode(author)
        tag.title = unicode(title)
        tag.album = unicode(album)
        tag.save()
    except NotImplementedError as ex:
        print "Couldn't add tag to %s, error was %s" % ( filepath, ex )
    except Exception as ex:
        print "Save tag failed, error was ", ex


if __name__ == '__main__':

    #Get the rss feed with the list of items
    if len(sys.argv) < 2:
        print "Error: you didn't give the xml file with the RSS info. Exiting."
        exit()

    rss_xml = open(sys.argv[1])
    parser = BeautifulStoneSoup(rss_xml.read())
    rss_xml.close()

    episodes = parser.findAll("item")

    for podcast in episodes:
        #mp3s only - skip the videos
        if podcast.enclosure['type'] != u'audio/mpeg':
            continue

        #Get the podcast attributes
        title = str(podcast.title.string)
        url = str(podcast.guid.string)
        author = str(podcast.find('itunes:author').string)

        output_filepath = generateFilepath(generateFilename(title, url))

        #download and tag the file
        if fetchContent(output_filepath, url):
            addTags(output_filepath, title, author, "YogaJournal Podcast")