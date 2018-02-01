import redis

r = redis.Redis()
base = 0 # Smallest allowed key in samples
jump = 50 # Key size bins
top = 1300 # Largest allowed key in sample
samples = 1000 # Numbers of samples

bins = []
for i in xrange(1+(top-base)/jump):
  bins.append({'count':0,'ttl':0,'idle':0,'volatile':0})

found = 0
for i in range(samples):
    k = r.randomkey()
    idle = r.object("idletime", k) # Must read idle time first before accessing the key
    if not r.type(k) == 'string':
        continue
    l = r.strlen(k)
    if l < base or l > top:
        continue
    found += 1
    ttl = r.ttl(k)
    b = bins[(l - base)/jump]
    b['count'] += 1
    if ttl is not None:
        b['ttl'] += ttl
        b['volatile'] += 1
    b['idle'] += idle

start = base
print "Skipped %d keys"%(samples - sum([b['count'] for b in bins]))
print '%-13s %-10s %-10s %-10s %-10s'%('Size range', 'Count', 'Volatile', 'Avg TTL', 'Avg idle')
for b in bins:
    if b['count']:
        print "%-13s %-10d %-10d %-10d %-10d"%('%d-%d'%(start, start+jump-1), b['count'], b['volatile'], b['ttl']/b['volatile'] if b['volatile'] else 0, b['idle']/b['count'])
    start += jump