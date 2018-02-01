#!/usr/bin/env python

import sys, subprocess, json, os
from pprint import pprint

if __name__ == "__main__":

    if 'AWS_SSH_KEY_FILE' in os.environ:
      key_path = os.environ['AWS_SSH_KEY_FILE']
    else:
      key_path = '~/.ssh/id_rsa'
    ssh_port = 22

    cmd = 'aws --profile {0} ec2 describe-instances --query "Reservations[].Instances[].[Tags,PublicIpAddress,PrivateIpAddress,VpcId]"'.format(os.environ['CHEFENV'])
    print "Running: ", cmd
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = proc.communicate()[0]

    tmp_vms = json.loads(out)
    vms = {}

    for vm in tmp_vms:
        if vm[0] != None and vm[1] != None and 'Key' in vm[0][0] and vm[0][0]['Key'] == 'Name':
            try:
                if os.environ['EC2_USE_PUBLIC_IP'] == True or int(os.environ['EC2_USE_PUBLIC_IP']) == 1:
                    vms[vm[0][0]['Value']] = vm[1]
                else:
                    vms[vm[0][0]['Value']] = vm[2]
            except Exception:
                vms[vm[0][0]['Value']] = vm[2]

    if len(vms) == 0:
        print "Error: No VMs exist"
        sys.exit(0)

    if len(sys.argv) < 2:
        print "Usage: ./aws-connect [HOSTNAME] [SSH_USERNAME]"
        sys.exit(0)

    if len(sys.argv) == 2:
        username = os.environ['USER']
    else:
        username = sys.argv[2]

    for vm_name, ip in vms.iteritems():

        if vm_name == sys.argv[1]:

            cmd = "ssh -o UserKnownHostsFile=/dev/null -o CheckHostIP=no -o StrictHostKeyChecking=no -i {0} -p {1} {2}@{3}".format(key_path, ssh_port, username, ip)
            print "Running: {0}".format(cmd)
            sys.exit(subprocess.call(cmd, shell=True))

    print "Error: VM not found!\n"