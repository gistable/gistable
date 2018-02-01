#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact : jbd at jbdenis dot net

import xml.etree.ElementTree
import re
import threading
import subprocess
import shlex
import os
import sys
import time

NAME_PREFIX = 'sge_queue_'

QUEUES_STATS = dict()
PARAMS = dict()  


# stolen from Forest http://stackoverflow.com/questions/1191374/subprocess-with-timeout
def kill_proc(proc, timeout):
    """ helper function for run """
    timeout["value"] = True
    proc.kill()


# stolen from Forest http://stackoverflow.com/questions/1191374/subprocess-with-timeout
def run(cmd, timeout_sec=10):
    """ run function with a timeout """
    try:
        proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError, err:
        return 1, "", "%s : %s" % (cmd, str(err)), False

    timeout = {"value": False}
    timer = threading.Timer(timeout_sec, kill_proc, [proc, timeout])
    timer.start()
    stdout, stderr = proc.communicate()
    timer.cancel()
    return proc.returncode, stdout.decode("utf-8"), stderr.decode("utf-8"), timeout["value"]

_Worker_Thread = None                                                                
_Lock = threading.Lock() # synchronization lock  

class UpdateMetricThread(threading.Thread):
    def __init__(self, params):
        threading.Thread.__init__(self)
        self.running      = False                                                    
        self.shuttingdown = False                                                    
        self.refresh_rate = 10                                                       
        if "refresh_rate" in params:                                                 
            self.refresh_rate = int(params["refresh_rate"])                          
        self.metric       = {}   

    def shutdown(self):                                                              
        self.shuttingdown = True                                                     
        if not self.running:                                                         
            return                                                                   
        self.join()                                                                  
                                                                                     
    def run(self):                                                                   
        self.running = True                                                          
                                                                                     
        while not self.shuttingdown:                                                 
            _Lock.acquire()                                                          
            self.update_metric()                                                     
            _Lock.release()                                                          
            time.sleep(self.refresh_rate)                                            
                                                                                     
        self.running = False                                                         

    def update_metric(self):
        self.metric = parse_qstat_queues()


    def metric_of(self, name):
        if self.metric is None:
            return 0
        name_parser = re.match("^%s(.*)_(.*)$" % NAME_PREFIX, name)
        if not name_parser:
            return 0
        try:
            qname = name_parser.group(1)
            sname = name_parser.group(2)
            _Lock.acquire()
            val = self.metric[qname][sname]
            _Lock.release()
            return val
        except IndexError:
            return 0
    


def check_params():
    if 'sgeroot' not in PARAMS or 'qstat' not in PARAMS:
	print >> sys.stderr, "You need to provide sgeroot and qstat parameters in configuration or via command line parameters"
	return False

    if not os.path.exists(PARAMS['sgeroot']):
	print >> sys.stderr, "%s does not exist" % PARAMS['sgeroot']
	return False

    if not (os.path.isfile(PARAMS['qstat']) and os.access(PARAMS['qstat'], os.X_OK)):
	print >> sys.stderr, "%s is not executable" % PARAMS['qstat']
	return False

    return True


def parse_qstat_queues():
    cmd = '/bin/env SGE_ROOT=%s %s -g c -xml' % (PARAMS['sgeroot'], PARAMS['qstat'])
    ret, out, err, timeout = run(cmd, 120)
    if ret != 0 or timeout:
        print err
        return None
    root = xml.etree.ElementTree.fromstring(out)
    queues = {}

    big_total = 0
    big_available = 0
    big_used = 0
    big_disabled = 0
    big_manual = 0

    for queue in root.findall('cluster_queue_summary'):
        try:
            name = queue.find('name').text
            queues[name] = {
                'load' : float(queue.find('load').text),
                'used' : int(queue.find('used').text),
                'resv' : int(queue.find('resv').text),
                'available' : int(queue.find('available').text),
                'total' : int(queue.find('total').text),
                'disabled' : int(queue.find('temp_disabled').text),
                'manual' : int(queue.find('manual_intervention').text)
            }
            big_total += queues[name]['total']
            big_available += queues[name]['available']
            big_used += queues[name]['used']
            big_disabled += queues[name]['disabled']
            big_manual += queues[name]['manual']
        except AttributeError, err:
            print err
            continue

    queues["globalstatistics"] = { 'total' : big_total,
                                   'available' : big_available,
                                   'used' : big_used,
                                   'disabled' : big_disabled,
                                   'manual' : big_manual 
                                 }

    return queues


def metric_of(name):
    return _Worker_Thread.metric_of(name)


def metric_init(params):
    """ Initialize metric descriptors """
    global PARAMS, _Worker_Thread
    for key in params:
        PARAMS[key] = params[key]

    if not check_params():
	    sys.exit(42)

    queues = parse_qstat_queues()
    descriptors = list()

    for qname, qvalues in queues.iteritems():
        for sname, svalue in qvalues.iteritems():
            if sname == 'load': continue
            desc = {
                    'name': NAME_PREFIX + qname + '_' + sname,
                    'groups': 'Open Grid Scheduler metrics',
                    'call_back' : metric_of,
                    'time_max': 60,
                    'value_type': 'uint',
                    'units': 'slots',
                    'slope': 'both',
                    'format': '%d',
                    'description:' : 'Slots available for %s queue' % qname
                    }
            descriptors.append(desc)

    _Worker_Thread = UpdateMetricThread(params)                                      
    _Worker_Thread.start() 

    return descriptors

def metric_cleanup():
    """Cleanup"""
    _Worker_Thread.shutdown()
    pass

def main():
    import getopt

    global PARAMS

    usage = "%s [--sgeroot path] [--qstat path]"
    try:
    	opts, args = getopt.getopt(sys.argv[1:], "", ["help", "sgeroot=", "qstat="])
    except getopt.GetoptError, err:
        print >> sys.stderr, str(err) # will print something like "option -a not recognized"
        print >> sys.stderr, usage
        sys.exit(2)

    for o, a in opts:
	if o == '--help':
  	    print >> sys.stderr, usage
	    sys.exit()
	elif o == '--sgeroot':
	    PARAMS['sgeroot'] = a
	elif o == '--qstat':
	    PARAMS['qstat'] = a

    
    descriptors = metric_init(PARAMS)
    try:
        while True:
            for d in descriptors:
                print (('%s = %s') % (d['name'], d['format'])) % (d['call_back'](d['name']))
            time.sleep(5)
    except KeyboardInterrupt:
        time.sleep(0.2)
        _Worker_Thread.shutdown()
        os._exit(1)
    except:
        print sys.exc_info()[0]
        _Worker_Thread.shutdown()
        raise

if __name__ == '__main__':
    main()
    
