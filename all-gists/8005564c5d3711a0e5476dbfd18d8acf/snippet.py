import csv
import threading
from Queue import Queue
from getpass import getpass
from netmiko import ConnectHandler
from datetime import datetime

USER = 'pyclass'
PASSWORD = getpass()


def ssh_session(row, output_q):

    output_dict = {}
    hostname = row['hostname']

    router = {'device_type': 'cisco_ios', 'ip': hostname, 'username': USER, 'password': PASSWORD, 'verbose': False, }
    ssh_session = ConnectHandler(**router)
    output = ssh_session.send_command("show version")

    # Add data to the queue
    output_dict[hostname] = output
    output_q.put(output_dict)


if __name__ == "__main__":

    print datetime.now()

    output_q = Queue()
    outfile = open('vlan2config.conf', 'w')
    
    with open('routers.csv') as routerFile:
        routerDict = csv.DictReader(routerFile)
        for row in routerDict:

            # Start all threads
            print row
            my_thread = threading.Thread(target=ssh_session, args=(row, output_q))
            my_thread.start()

    # Wait for all threads to complete
    main_thread = threading.currentThread()
    for some_thread in threading.enumerate():
        if some_thread != main_thread:
            some_thread.join()

    # Retrieve everything off the queue
    while not output_q.empty():
        my_dict = output_q.get()
        for k, val in my_dict.iteritems():
            print k
            print val

            # Write info to file
            #outfile.write(output)
    
    outfile.close()
    print datetime.now()