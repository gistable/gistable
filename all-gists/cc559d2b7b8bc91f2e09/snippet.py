#!/usr/bin/env python

description = """\
Usage: BaseSpaceRunDownloader_v2.py -r <ProjectName> -a <AccessToken>

This is a modified version of the BaseSpace Python Run Downloader from Illumina. It takes 
the project name (instead of the run id) and downloads base calls as fastq files (instead of
the image/intensity data).

It also checks that the sizes of the downloaded files match with what's reported by the 
BaseSpace REST API. Downloaded files are organised by project/sample/file, just like in the 
BaseSpace Downloader GUI app.

There's rudimentary support for resuming interrupted transfers. The script does not download
a file if there's a file with matching size already on the disk. Partially downloaded files 
where the size of the local file does not match the BaseSpace REST API are detected as size
mismatches, but need to be examined/removed manually.

References
Original Illumina code: https://support.basespace.illumina.com/knowledgebase/articles/403618-python-run-downloader
BaseSpace REST API: https://developer.basespace.illumina.com/docs/content/documentation/rest-api/api-reference
Heng Li's notes on BaseSpace: https://gist.github.com/lh3/54f535b11a9ee5d3be8e
"""
from urllib2 import Request, urlopen, URLError
import json
import math
import sys
import os
import socket
import optparse
import pprint
import itertools

def arg_parser():
    cwd_dir = os.getcwd()
    parser = optparse.OptionParser()
    parser.add_option( '-r', dest='runid', help='Run ID: required')
    parser.add_option( '-a', dest='accesstoken', help='Access Token: required')
    ( options, args ) = parser.parse_args()
   
    try:
       if options.runid == None:
             raise Exception
       if options.accesstoken == None:
	     raise Exception

    except Exception:
	    print description
	    sys.exit()
    
    return options

def restrequest(rawrequest):
	request = Request(rawrequest)

	try:
        	response = urlopen(request)
        	json_string = response.read()
        	json_obj = json.loads(json_string)

	except URLError, e:
    		print 'Got an error code:', e
		sys.exit()

	return json_obj

def downloadrestrequest(rawrequest,path):
	#dirname = RunID + os.sep + os.path.dirname(path)
	dirname = os.path.dirname(path)

	if dirname != '':
		if not os.path.isdir(dirname):
			os.makedirs(dirname)
	
	request = (rawrequest)

	#outfile = open(RunID + os.sep + path,'wb')
	outfile = open(path,'wb')

        try:
                response = urlopen(request,timeout=1)
		
		outfile.write(response.read())
		outfile.close()

        except URLError, e:
                print 'Got an error code:', e
		outfile.close()
		downloadrestrequest(rawrequest,path)


	except socket.error:
		print 'Got a socket error: retrying'
		outfile.close()
		downloadrestrequest(rawrequest,path)
		
options = arg_parser()

RunID = options.runid
AccessToken = options.accesstoken

# Given project name (stored in RunID), find the project ID
request = 'http://api.basespace.illumina.com/v1pre3/users/current/projects?access_token=%s&limit=1000' % (AccessToken,)
json_obj = restrequest(request)
for project in json_obj['Response']['Items']:
    if project['Name'] == RunID:
        (ProjectName, ProjectID) = (project['Name'], project['Id'])
        ProjectDir = "%(ProjectName)s-%(ProjectID)s" % locals()
print ProjectDir

# Get a list of sample IDs in a given project (yes, this barfs with >1000 samples)
request = 'http://api.basespace.illumina.com/v1pre3/projects/%s/samples?access_token=%s&limit=1000' %(ProjectID,AccessToken)
json_obj = restrequest(request)
for sample in itertools.islice(json_obj['Response']['Items'], None):
    (SampleName, SampleID) = (sample['Name'], sample['Id'])
    SampleDir = os.path.join(ProjectDir, "%(SampleName)s-%(SampleID)s" % locals())
    print SampleDir

    sample_request = 'http://api.basespace.illumina.com/v1pre3/samples/%s/files?access_token=%s' %(sample['Id'],AccessToken)
    sample_json_obj = restrequest(sample_request)
    for sample_file in itertools.islice(sample_json_obj['Response']['Items'], None):
        FilePath = os.path.join(SampleDir, sample_file['Path'],)
        print FilePath,
        if not os.path.isfile(FilePath):
            file_request = 'http://api.basespace.illumina.com/%s/content?access_token=%s'%(sample_file['Href'],AccessToken)
            downloadrestrequest(file_request, FilePath)

        if sample_file['Size'] == os.path.getsize(FilePath):
            print 'size_ok'
        else:
            print 'size_mismatch'
            sys.exit('File sizes differ between disk and BaseSpace for %(FilePath)s' % locals())
