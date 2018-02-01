# Meant to allow you to grab and save 1 minute videos at any given moment while watching something on Plex. 
# This also saves it to Dropbox.  It needs to be run locally.
# This has a few dependencies.  Needs moviepy, ffmpeg, anddddddd I think that's it.  

import os
import urllib
import urllib2
import xml.etree.ElementTree as etree

from moviepy.editor import *
from moviepy.video.tools.cuts import find_video_period
from moviepy.audio.tools.cuts import find_audio_period	
import random
import string

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

# This is connecting to my LOCAL plex server.  It needs to run locally.  
response = urllib.urlopen("http://10.0.1.2:32400/status/sessions")
xmlContent = response.read()
#print xmlContent
xmlTree = etree.fromstring(xmlContent)

if xmlTree.find('Video') is None:
    print "Nothing is playing."

else:

	for child in xmlTree.iter('Video'):
		#print child.find('Media/Part').get('file', 0)

		plexViewCount = child.get('viewOffset', 0)
		fileLocation = child.find('Media/Part').get('file', 0)
		#partNode = mediaNode.find('Part')
		#fileLocation = partNode.get('file', 0)
		print fileLocation
		#fileLocation = "/Users/myUserName/Downloads/Spookies.avi" # ---> Temporary, meant to be removed.

		filename = fileLocation.split("/")[-1]
		print "Filename:  " + filename

		# Gets the current playback location and removes the milliseconds for simplicity
		plexViewCount = plexViewCount[:-3]
		print "Current Playhead Location in seconds:  " + str(plexViewCount)

		# Only for printing out the playehead, checking for accuracy, not otherwise necessary.
		minutes, seconds= divmod(int(plexViewCount), 60)
		print "Current Playhead Location:  " +  str(minutes) + ":" + str(seconds)

		# Creates the temp media and final file.  I had to create a temp-audio.m4a file because for whatever reason, ffmpeg required it to create the AAC.
		video1 = VideoFileClip(fileLocation)
		W,H = video1.size
		# This is grabbing 30 seconds before and 30 seconds after the moment you execute the script.  The idea is you'll get a one minute clip total.
		subclipVideo = video1.subclip(int(plexViewCount)-30, int(plexViewCount)+30)
		homePath = os.path.expanduser('~')
		filePath = homePath + "/Dropbox/Video Moments/" + filename.split(".")[0] + "_" + id_generator(5) + ".mp4"
		print filePath
		tempPath = homePath + "/Desktop/temp-audio.m4a"
		subclipVideo.write_videofile(filePath, temp_audiofile=tempPath, remove_temp=True, codec="libx264", audio_codec="aac")