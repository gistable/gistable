import re
import pickle
from threading import Timer
import subprocess
from subprocess import call
import os.path
import sys

# config
database = 'allPairs.p'
channels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

if len(sys.argv) > 1:
	database = sys.argv[1]
if len(sys.argv) > 2:
	channels = sys.argv[2:len(sys.argv)]

# run
hopTime = 10

airport = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'

call(['networksetup',
	'-setairportpower',
	'airport', 'on'])

call(['sudo',
	airport,
	'--disassociate'])

channelIndex = int(0)
def hopChannels():
	global channelIndex
	channelIndex += 1
	if channelIndex == len(channels):
		channelIndex = 0
	channel = channels[channelIndex]
	print('hopping to channel ' + str(channel))
	call(['sudo',
		airport,
		'--channel=' + str(channel)])
	Timer(hopTime, hopChannels).start()
hopChannels()

allPairs = set();

if os.path.isfile(database):
	print('loading database from disk')
	allPairs = pickle.load(open(database, "rb"))

p = subprocess.Popen(('sudo',
	'tcpdump', '-l', '-e', '-I',
	'type mgt subtype probe-req'),
	stdout=subprocess.PIPE)
try:
	for row in p.stdout:
		result = row.decode('utf-8')
		pattern = re.compile('SA:(.+) \(oui Unknown\) Probe Request \((.+)\) ');
		m = pattern.search(result)
		if m:
			print(m.group(1) + ' @ ' + m.group(2))
			allPairs.add((m.group(1), m.group(2)))
			pickle.dump(allPairs, open(database, "wb"))
except KeyboardInterrupt:
	p.terminate()
	call(['networksetup',
		'-setairportpower',
		'airport', 'off'])