#!/usr/bin/python
import sys, time, datetime, os, pwd

# Get Arguments
numArgs = len(sys.argv)
# First argument Number to Call
try:
	sys.argv[1]
	asteriskParams = {'numbertocall':sys.argv[1], 
	'context': 'itp-redial',
	'extension':'s', 
	'variables':'', 
	'touchtime':''}
except:
	print 'USAGE: gencallfile.rb [phone-number] [context] [exten] [varname=value] [hour-minute-second-month-day-year]\n'
	sys.exit()

if numArgs>2:
	asteriskParams['context']=sys.argv[2]
	if numArgs>3:
		asteriskParams['extension']=sys.argv[3]
		if numArgs>4:
			asteriskParams['variables']==sys.argv[4]
			if numArgs>5:
				asteriskParams['touchtime']==sys.argv[5]

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S-%m-%d-%Y')

temp_dir = "/tmp/"
callfile = "call_" + st + ".call"
startcallfile = temp_dir + callfile
end_dir = "/var/spool/asterisk/outgoing/"
endcallfile = end_dir + callfile
#write file to disk
scf = open(startcallfile,"w")
scf.write("Channel: SIP/flowroute/" + asteriskParams['numbertocall'] + "\n")
scf.write("MaxRetries: 1\n")
scf.write("RetryTime: 60\n")
scf.write("WaitTime: 30\n")
scf.write("Context: " + asteriskParams['context'] + "\n")
scf.write("Extension: " + asteriskParams['extension'] + "\n")
if asteriskParams['variables']!="":
	scf.write("Set: " + asteriskParams['variables'] + "\n")

scf.close()
#change file permission
os.chmod(startcallfile,0777)
os.chown(startcallfile, pwd.getpwnam(os.environ['USER']).pw_uid, pwd.getpwnam(os.environ['USER']).pw_gid)

#hour-minute-second-month-day-year (example: 02-10-00-09-27-2007)
if asteriskParams['touchtime'] != "":
	ctime = time.mktime(datetime.datetime.strptime(asteriskParams['touchtime'], "%H:%M:%S-%m-%d-%Y").timetuple())
	os.utime(startcallfile,ctime,ctime,) #change file time to future date

#move file to /var/spool/asterisk/outgoing
os.rename(startcallfile, endcallfile)


