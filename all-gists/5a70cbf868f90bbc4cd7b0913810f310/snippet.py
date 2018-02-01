import subprocess
import os
import re
import sys
import argparse
import httplib, urllib
import time

"""
# place this file at /home/ethos/check_hash_reboot.py
# The entries at the bottom of this comment block go into the crontab for the ethos user

# this uses pushover to notify you about reboots etc.
# replace <app_token> with your app token, eg. curl -s -F "token=as9dv8jaw4e9fasdjgoa2w3t98jawl4" ...
# replace <user_token> with your user token eg. ... -F "user=rtsfgjsrtjsrtj457ujtfgtwsvka" ...

## notifies you when EthOS is back up
@reboot curl -s -F "token=<app_token>" -F "user=<user_token>" -F "title=ethos back up" -F "message=Rebooted but now back up" https://api.pushover.net/1/messages.json

## runs this script every minute and passes in pushover tokens and pipes to log file 
 * * *   *    *   /usr/bin/python /home/ethos/check_hash_reboot.py -u <user_token> -a <app_token>  >> /home/ethos/check_hash_reboot.log
"""
# Send a message using the pushover notification service
def pushover_message(title, message, app_token, user_token):
	conn = httplib.HTTPSConnection("api.pushover.net:443")
	conn.request("POST", "/1/messages.json",
	  urllib.urlencode({
	    "token": app_token,                       # Insert app token here
	    "user": user_token,                       # Insert user token here
	    "title": title,                			  # Title of the message
	    "message": message     				      # Content of the message
	  }), { "Content-type": "application/x-www-form-urlencoded" })
	return conn.getresponse()

# parse the passed arguments
parser = argparse.ArgumentParser()

parser.add_argument(
	'-f',
	'--checkfilepath',
	dest='check_file_path', 
	help="path to store temporary file at if reboot criteria is met, but we need to wait until next time this script runs, check if that file exists, criteria are till met and then reboot",	
	default="/tmp/reboot_conditions_met_last_time.txt"
)

parser.add_argument('-a', '--pushover_app_token', dest='pushover_app_token',  help="app token for pushover service for push notifications on reboot")

parser.add_argument('-u', '--pushover_user_token', dest='pushover_user_token',  help="user token for pushover service for push notifications on reboot")

args = parser.parse_args()

# call the update command from EthOs, which outputs current status, including hashrate
update_data = subprocess.check_output(['/opt/ethos/bin/update'])

hash = None
miner_id = ''

# loop through the output of the update command, to parse the hashrate
for line in update_data.splitlines():
	if 'hash:  ' in line:
		hash_line = line
		hash_list = re.findall(r'\d+\.\d+', hash_line)

		# if we don't get a 2 decimal number, then it is probably crashed
		if len(hash_list) > 0:
			hash = float(hash_list[0])

	# store the hostname to add to the push notification
	elif 'hostname:   ' in line:
		hostname_list = re.findall(r'\w+', line)
		if len(hostname_list) > 1:
			miner_id = hostname_list[1]
# debugging output
print time.ctime()
print hash

# start doing stuff if the hash is non-existant of less than 10
if not hash or hash < 10:
	print "hash is zero"
	#criteria are met
	#check if file exists, meaning that conditions were met last time
	if os.path.isfile(args.check_file_path):
		print 'file here'
		os.remove(args.check_file_path)
		# send push notification if the tokens have been set
		if args.pushover_user_token and args.pushover_app_token:
			pushover_message(
				'Miner {} restarted'.format(miner_id),
				'Miner {} reached hash rate of 0'.format(miner_id),
				args.pushover_app_token,
				args.pushover_user_token
			)
		# reboot the system
		os.system("/opt/ethos/bin/r")
	else:
                print "making file {}".format(args.check_file_path)
		# create a file so that next time we know if has been at state for a while
		os.system('touch {}'.format(args.check_file_path))
else:
	print "Hash is good"
	# if the checkfile exists, remove it because the conditions are no longer met
	if os.path.isfile(args.check_file_path):
		os.remove(args.check_file_path)
