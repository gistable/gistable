################################################################################################
#
#	Script to organize pictures uploaded from Mobile Devices to Dropbox's Camera Upload folder
#
#	Daniel Spillere Andrade - www.danielandrade.net
#
################################################################################################

import os, time
import glob
 
#Define Pictures Folder
#You may have to change this!
folder = '/Users/admin/Dropbox/Camera Uploads/'
 
fileFormats = ['JPG','jpg', 'MOV', 'mov', 'PNG', 'png', 'mp4', 'MP4'];
months = ['January','February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
picPath = []
 
#Generate list of files
for formats in fileFormats:
	picPath = picPath + glob.glob(folder + "*."+formats)
 
for files in picPath:
	picName = files.split('/')
	filename = picName[-1][:-4].split(' ')
	date = filename[0].split('-')
	hour = filename[1]

	dateYear = date[0]
	dateMonth = date[1]
	dateDay = date[2]
	month = months[int(dateMonth)-1]
	monthNum = str(int(dateMonth)).zfill(2) 

	#folder exists? if not, create them!
	if not os.path.exists(folder + dateYear):
	    print 'Making dir:' + folder + dateYear
	    os.makedirs(folder + dateYear)
	if not os.path.exists(folder + dateYear + '/' + monthNum + '-' + month):
	    print 'Making dir:' + folder + dateYear + '/' + monthNum + '-' + month
	    os.makedirs(folder + dateYear + '/' + monthNum + '-'  +month)

 
	#Move files
	print 'Movendo: ' + files + ' --> ' +  folder + dateYear + '/' + monthNum + '-' + month + '/'
	os.rename(picName[-1],folder + dateYear + '/' + monthNum + '-' + month + '/' + picName[-1])
	
print "Done :)"
