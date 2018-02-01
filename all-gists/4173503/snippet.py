import re
import os
import sys

ip_re = re.compile(r'.* has address .*')
ec2 = re.compile(r'ec2-')

def ip_to_ec2(ip):
    output = os.popen('host ' + ip).read()
    hostname = output.split(' ')[4].rstrip()
    
    if ec2.search(hostname) is not None:
        return hostname
    else:
        return None
    
    
###############################################################################
#  MAIN PROGRAM                                                               #
###############################################################################
if len(sys.argv) != 2:
    print 'Usage: ec2_host_names.py domain_file'
    sys.exit(1)
    
outfile = open(sys.argv[1].split('.')[0] + '_ec2_hosts.txt', 'w')

count = 1
for line in open(sys.argv[1]):
    host = line.rstrip()
    
    if count % 100 == 0: print '{0} {1}'.format(count, host)
    
    output = os.popen('host ' + line).read()
  
    for text in output.split('\n'):
        if ip_re.search(text) is not None:
            ip = text.split(' ')[3].rstrip()
            ec2_name = ip_to_ec2(ip)
            if ec2_name is not None:
                outfile.write('{0} {1}\n'.format(host, ec2_name))
                outfile.flush()
    
    count += 1
    
outfile.close()
