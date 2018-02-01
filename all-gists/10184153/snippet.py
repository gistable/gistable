import os
import pprint
import fnmatch
import time
import subprocess

def find_services_needing_restart():
    services = {}
    pids = [ f for f in os.listdir('/proc') if f.isdigit() and os.path.isdir(os.path.join('/proc', f)) ]

    for pid in pids:
        reasons = set()
        try:
            with open('/proc/{0}/maps'.format(pid), 'r') as maps:
                for map in maps.readlines():
                    if '(deleted)' in map and '/usr/lib' in map:
                        reasons |= set([map])
            if len(reasons) > 0:
                with open('/proc/{0}/cgroup'.format(pid), 'r') as cgroups:
                    for cgroup in cgroups.readlines():
                        if 'systemd' in cgroup:
                            service = cgroup.strip().split('/')[-1]
                            if service != '':
                                 services[service] = reasons
        except IOError as e:
            print('PID {0} went away (or permission denied): {1}'.format(pid, e))
    return services

def find_matches(services, whitelist):
    matches = set()
    for whitelist_item in whitelist:
        restart_services = fnmatch.filter(services, whitelist_item)
        matches |= set(restart_services)
    return matches

def restart_services(services):
    for service in services:
        print('Restarting {0}...'.format(service))
        result = subprocess.check_output(['/usr/bin/systemctl', 'restart', service], stderr=subprocess.STDOUT)
        print(result)
        print('    ...done')
        time.sleep(5)

services = set(find_services_needing_restart().keys())

whitelist = ['*.service']
whitelisted = find_matches(services, whitelist)
print('Restarting:')
pprint.pprint(whitelisted)

print('Not Restarting:')
pprint.pprint(services.difference(whitelisted))

restart_services(whitelisted)