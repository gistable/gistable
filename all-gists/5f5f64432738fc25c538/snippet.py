#!/usr/bin/env python
import sys
import msfrpc
import time

if __name__ == '__main__':
    # Create a new instance of the Msfrpc client with the default options
    client = msfrpc.Msfrpc({})

    # Login to the msf server using the password "abc123"
    client.login(user='msf', password='mypass')

    # list all auxiliary modules
    #  mod = client.call('module.auxiliary')
    #  for i in (mod.get('modules')):
    #      print i

    res = client.call('console.create')
    console_id = res['id']
    print "res: %s" %res
    
    a = client.call('console.write', [console_id, "db_connect msf:myotherpass@127.0.0.1/msf\n"])
    time.sleep(1)
    a = client.call('console.write', [console_id, "workspace -a ssh_version_tester\n"])
    time.sleep(1)
    a = client.call('console.write', [console_id, "set THREADS 10\n"])
    time.sleep(1)
    a = client.call('console.write', [console_id, "workspace ssh_version_tester\n"])
    time.sleep(1)
    a = client.call('console.write', [console_id, "use auxiliary/scanner/ssh/ssh_version\n"])
    time.sleep(1)
    a = client.call('console.write', [console_id, "set RHOSTS file:/tmp/ssh_hosts.txt\n"])
    time.sleep(1)
    a = client.call('console.write', [console_id, "run\n"])
    time.sleep(5)
    
        while True:
        res = client.call('console.read',[console_id])
        if len(res['data']) > 1:
            print res['data'],

        if res['busy'] == True:
            time.sleep(1)
            continue

        break

    cleanup = client.call('console.destroy',[console_id])
    print "Cleanup result: %s" %cleanup['result']