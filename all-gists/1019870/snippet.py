import subprocess

def uptime():
    raw = subprocess.check_output('uptime').replace(',','')
    days = int(raw.split()[2])
    if 'min' in raw:
    	hours = 0
    	minutes = int(raw[4])
    else:
    	hours, minutes = map(int,raw.split()[4].split(':'))
    totalsecs = days*24*60*60 + hours*60*60 + minutes*60    
    return totalsecs
    
print 'System uptime of %d seconds' % (uptime())
