import urllib2
import time

listOfURLS = "myFile.txt"

with open(listOfURLS) as input_file:
    for i, line in enumerate(input_file):
    	data = urllib2.urlopen(line).read()
    	filename = "path/to/folder"+line+".txt"
        file(fileName, "w").write(data)
        print "Done - " + fileName
        time.sleep(1)