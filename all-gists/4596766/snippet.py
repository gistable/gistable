#!/usr/bin/env python

#install the follow first:

#sudo easy_install pip

#sudo pip install -U boto

#sudo pip install configparser

#sudo pip install gitpython

#sudo pip install requests

#sudo pip install certifi

#sudo pip install netdnarws

#then setup the config files in your root user directory. these files store your api information for s3 and maxcdn

#.aws file should look like this: https://gist.github.com/4596753

#.maxcdn file should look like this: https://gist.github.com/4596743

import git, os, sys, boto, mimetypes, ConfigParser

from pprint import pprint

from boto.s3.key import Key

debug = True

repo = git.repo.base.Repo()

#check to see if there are any uncommited changes

if repo.is_dirty() and not debug:

  print "\nERROR: COMMIT YOUR CHANGES BEFORE DEPLOYING.\n"
	
	sys.exit(os.EX_NOINPUT)
	
#switch to master

if repo.active_branch != 'master':

	os.system("git checkout master")
	
#pull the remote

os.system("git pull")

#get the latest commits

commit = None

for c in repo.iter_commits():

	commit = c
	
	break
	
#print commit.stats.files

files_to_deploy = []

for f in commit.stats.files:

	if f.find('_site') is 0:
	
		files_to_deploy.append(f)
		
#print files_to_deploy

#get s3 credentials from config file

S3_ACCESS_ID = None

S3_SECRET_KEY = None

if os.path.exists(os.path.expanduser('~/.aws')):

	config  =   ConfigParser.SafeConfigParser()

	config.readfp(open(os.path.expanduser('~/.aws')))
	
	if config.has_section('s3'):
	
		if config.has_option('s3', 'access_id'):
		
			S3_ACCESS_ID = config.get('s3', 'access_id')
			
			#print 'grabbed s3.access_id'
		
		else:
		
			print '.aws config file missing acess_id'
			
			sys.exit()
	
		if config.has_option('s3', 'secret_key'):
		
			S3_SECRET_KEY = config.get('s3', 'secret_key')
			
			#print 'grabbed s3.secret_key'
		
		else:
		
			print '.aws config file missing secret_key'
			
			sys.exit()
	
	else:
	
		print 'No s3 section in .aws config file'
		
		sys.exit()

else:

	print 'No .aws config file in user directory'
	
	sys.exit()

con = boto.connect_s3(S3_ACCESS_ID, S3_SECRET_KEY)

bucket = con.get_bucket('ofacontribute')

print 'uploading the following files to s3:'

print files_to_deploy

for f in files_to_deploy:

	#print f

	file_path = f.replace('_site/donation/', '')
	
	#print file_path

	k = Key(bucket = bucket, name = file_path)
	
	#mimetype = mimetypes.guess_type(f)[0]
	
	#print os.path.join(repo.working_dir, f)
	
	k.set_contents_from_filename(os.path.join(repo.working_dir, f), headers = {"Content-Type": 'text/html'})
	
	k.set_acl('public-read')

paths_to_purge = []

for f in files_to_deploy:

	#print f.replace('_site', 'https://contribute.barackobama.com')
	
	paths_to_purge.append(f.replace('_site', 'https://contribute.barackobama.com'))

print 'purging the following paths from the cdn:'

print paths_to_purge

MAXCDN_ALIAS = None

MAXCDN_CONSUMER_KEY = None

MAXCDN_CONSUMER_SECRET = None

if os.path.exists(os.path.expanduser('~/.maxcdn')):

	config  =   ConfigParser.SafeConfigParser()

	config.readfp(open(os.path.expanduser('~/.maxcdn')))
	
	if config.has_section('maxcdn'):
	
		if config.has_option('maxcdn', 'alias'):
		
			MAXCDN_ALIAS = config.get('maxcdn', 'alias')
			
			print 'found maxcdn.alias'
		
		else:
		
			print '.maxcdn config file missing alias'
			
			sys.exit()
	
		if config.has_option('maxcdn', 'consumer_key'):
		
			MAXCDN_CONSUMER_KEY = config.get('maxcdn', 'consumer_key')
			
			print 'found maxcdn.consumer_key'
		
		else:
		
			print '.maxcdn config file missing consumer_key'
			
			sys.exit()

		if config.has_option('maxcdn', 'consumer_secret'):
		
			MAXCDN_CONSUMER_SECRET = config.get('maxcdn', 'consumer_secret')
			
			print 'found maxcdn.consumer_secret'
		
		else:
		
			print '.maxcdn config file missing consumer_secret'
			
			sys.exit()
	
	else:
	
		print 'No maxcdn section in .maxcdn config file'
		
		sys.exit()

else:

	print 'No .maxcdn config file in user directory'
	
	sys.exit()

from netdnarws import NetDNA

api = NetDNA(MAXCDN_ALIAS, MAXCDN_CONSUMER_KEY, MAXCDN_CONSUMER_SECRET)

for f in paths_to_purge:

	api.delete('/zones/pull.json/33242/cache?file=' + f, debug=True)

print "\nSUCCESS\n"
