
"""
- sequence read
- sequence write 
"""

import os
import sys
import time
import errno
import time 
import threading 
import qfs
import Queue 
import sys 
sourceQueue = Queue.Queue()

def ParseConfig(config):
    host = ''
    port = -1
    for line in open("qfssample.cfg"):
        if line.startswith("#") or len(line.strip()) == 0:
            continue
        s = line.strip()
        if s.split('=')[0].strip() == 'metaServer.name':
            host = s.split('=')[1].strip()
        elif s.split('=')[0].strip() == 'metaServer.port':
            port = int(s.split('=')[1].strip())
    if (host,port) == ('', -1):
        sys.exit('Failed to parse config file')
    return (host,port)


def createDirectories(Client, Url, parentFolder):
	LF   = Url.split('/')
	lenL = len (LF)
	index = 0
	for i in LF:
		if(index  < lenL - 1 and i != None and i != ''):
			parentFolder = parentFolder + i + "/"
			try:
				Client.mkdir(parentFolder)
				print "Create %s" %(parentFolder)
			except IOError, err:
				pass
		index = index + 1
		
class ReadThread(threading.Thread):
	def __init__(self, inputFile, sourceQueue):
		threading.Thread.__init__(self) 
		self.inputFile   = inputFile 
		self.sourceQueue =  sourceQueue 
	def run(self):
		fileContent = open(self.inputFile, 'r')
		while True:
			line = fileContent.readline() 
			if not line: break 
			self.sourceQueue.put(line) 
			

class WriteThread(threading.Thread):
	def __init__(self, inputQueue, Client):
		threading.Thread.__init__(self)
		self.inputQueue = inputQueue
		self.Client 	= Client 
	def processQueueItem(self):
		while True:
			if not self.inputQueue.empty(): item = self.inputQueue.get().strip()
			if item: 
				timeStart = time.time()
				photoFile = item.split('/')[-1]
				recursiveDir = item.replace(photoFile, '')  
				createDirectories(self.Client, recursiveDir, '/')
				self.Client.cd(recursiveDir) 
				dfsFile = self.Client.create(photoFile.split('.')[0], 1)
				binaryData = open(item, 'rb').read() 
				dfsFile.write(binaryData)
				dfsFile.sync()
				dfsFile.close()
				print "Read and write %s in %s" %(item, (time.time() - timeStart)) 
		

def main():
	if len(sys.argv) < 2:
		sys.exit('Usage: %s config_file' % sys.argv[0])
	client = None
	server = ParseConfig(sys.argv[1])
	listFile = "allPhoto.txt"
	f = open(listFile)
	try:
		client = qfs.client(server)
	except:
		print "Unable to start the QFS client."
		print "Make sure that the meta- and chunkservers are running."
		sys.exit(1)
	start = time.time() 
	# initialize queue 
	for i in range(10):
		reader = ReadThread(listFile, sourceQueue) 
		reader.setDaemon(True) 
		reader.run()
	for i in range(5): 
		writer = WriteThread(sourceQueue, client)
		writer.setDaemon(True)
		writer.processQueueItem()
	
	print "Read from MFS and write QFS  in %s seconds" %((time.time() - start))

	 
	
if __name__ == '__main__':
    main()
