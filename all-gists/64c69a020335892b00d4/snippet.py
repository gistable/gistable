import subprocess
import csv

def ping(hostname):
    p = subprocess.Popen('ping ' + hostname, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    pingStatus = 'ok';
        
    for line in p.stdout:
        output = line.rstrip().decode('UTF-8')
 
        if (output.endswith('unreachable.')) :
            #No route from the local system. Packets sent were never put on the wire.
            pingStatus = 'unreacheable'
            break
        elif (output.startswith('Ping request could not find host')) :
            pingStatus = 'host_not_found'
            break
        if (output.startswith('Request timed out.')) :
            #No Echo Reply messages were received within the default time of 1 second.
            pingStatus = 'timed_out'
            break
        #end if
    #endFor
    
    return pingStatus
#endDef    


def printPingResult(hostname):
    statusOfPing = ping(hostname)
    
    if (statusOfPing == 'host_not_found') :
        writeToFile('!server-not-found.txt', hostname)
    elif (statusOfPing == 'unreacheable') :
       writeToFile('!unreachable.txt', hostname)
    elif (statusOfPing == 'timed_out') :
       writeToFile('!timed_out.txt', hostname)	   
    elif (statusOfPing == 'ok') :
        writeToFile('!ok.txt', hostname)
    #endIf
#endPing


def writeToFile(filename, data) :
    with open(filename, 'a') as output:
        output.write(data + '\n')
    #endWith
#endDef    


'''
servers.txt example
   vm8558
   host2
   server873
   google.com
'''
file = open('servers.txt')

try:
    reader = csv.reader(file)
    
    for item in reader:
        printPingResult(item[0].strip())
    #endFor
finally:
    file.close()
#endTry
