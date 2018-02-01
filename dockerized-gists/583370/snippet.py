# NginxStats
# python nginxstats.py --servers="http://meuservido.com.br/nginx_status" --time=5

import os, sys, atexit, getopt
import re
import sys
import time
import urllib

class NginxStats():
    
    def __init__(self, servers, time):
        self.servers = servers
        self.prev = {'accepted':0, 'requests':0}
        self.total = {'connections':0, 'accepted':0, 'requests':0, 'reading':0, 'writing':0, 'waiting':0}
        self.count = 0
        
        self.TIME_SLEEP = time
    
    def parse(self, content):
        result = {}

        match1 = re.search(r'Active connections:\s+(\d+)', content)
        match2 = re.search(r'\s*(\d+)\s+(\d+)\s+(\d+)', content)
        match3 = re.search(r'Reading:\s*(\d+)\s*Writing:\s*(\d+)\s*'
            'Waiting:\s*(\d+)', content)
        if not match1 or not match2 or not match3:
            raise Exception('Unable to parse %s' % content)

        result['connections'] = int(match1.group(1))

        result['accepted'] = int(match2.group(1))
        result['requests'] = int(match2.group(3))

        result['reading'] = int(match3.group(1))
        result['writing'] = int(match3.group(2))
        result['waiting'] = int(match3.group(3))

        return result
        
    def get_stats(self):

        stats = {'connections':0, 'accepted':0, 'requests':0, 'reading':0, 'writing':0, 'waiting':0}
        for server in self.servers:
            data = urllib.urlopen(server)
            content = data.read()
            result = self.parse(content)
            for k,v in result.iteritems(): stats[k] += v
        
        return stats
    
    def loop(self):
        self.print_header()
        self.prev = self.get_stats()
        time.sleep(self.TIME_SLEEP)
        try:
            while True:
                nginx_stats = self.get_stats()
                self.print_stats(nginx_stats)
                self.prev = nginx_stats
                for k,v in self.total.iteritems(): self.total[k] += nginx_stats[k]
                self.count += 1
                time.sleep(self.TIME_SLEEP)
        except KeyboardInterrupt:
            self.print_footer()

    def print_stats(self, stats):
        print '%8d %10.2f %10.2f %5d %5d %5d' % (stats['connections'],
                                                float(stats['accepted'] - self.prev['accepted']) / self.TIME_SLEEP,
                                                float(stats['requests'] - self.prev['requests']) / self.TIME_SLEEP,
                                                stats['reading'],
                                                stats['writing'],
                                                stats['waiting'])

    def print_footer(self):
        print '-------- ---------- ---------- ----- ----- -----'
        print '%8d %10.2f %10.2f %5d %5d %5d' % tuple([v / self.count for k,v in self.total.iteritems()])
    
    def print_header(self):
        print '%-8s %-10s %-10s %-5s %-5s %-5s' % ('Conn', 'Conn/s', 'Request/s', 'Read', 'Write', 'Wait')
        print '-------- ---------- ---------- ----- ----- -----'
        

def usage():
    print "\nNginx Stats Monitor:"
    print "usage: nginxstats.py [--servers=HOST1,HOST2] [--time=TIME_SLEEP] [--help]"

def main():

    try:
        optlists, command = getopt.getopt(sys.argv[1:], "hst", ["help", "servers=", "time="])
    except getopt.GetoptError, err:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    servers = []
    time = 5
    
    for opt, value in optlists:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-s", "--servers"):
            servers = [s.strip() for s in value.split(",")]
        elif opt in ("-t", "--time"):
            time = int(value)

    nStats = NginxStats(servers, time)
    nStats.loop()

if __name__ == "__main__":
    main()
