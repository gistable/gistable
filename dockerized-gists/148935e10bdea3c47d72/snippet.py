#!/usr/bin/env python3

from argparse import ArgumentParser
from subprocess import Popen, PIPE, STDOUT
import shlex
import hashlib
import time
import warnings
import os, sys, io
import signal
import re

DELAY   = 10
DNSMASQ_DHCP_LEASE = "/var/lib/misc/dnsmasq.leases"
DNSMASQ_DDNS_HOSTS = "/etc/dnsmasq.hosts.d/ddns"
REMOTE_DNSMASQ_RESTART_COMMAND = "sudo systemctl restart dnsmasq"
REMOTE_DNSMASQ_UPDATE_DDNS_COMMAND = "sudo tee {0}"
SSH_CMD = "/usr/bin/ssh"
SSH_OPTIONS = ["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "-o", "ConnectTimeout=30"]
REMOTE_COMMAND_TIMEOUT = 10
VERSION = "1.0"

parser = ArgumentParser(description="foo")
parser.add_argument('--version', '-v', action='version', version='%(prog)s ' + VERSION)

parser.add_argument('--oneshot', '-1', action='store_true', help='execute once and end')
parser.add_argument('--servers', action='store', required=True, nargs='*', help='dnsmasq servers')
parser.add_argument('--ssh-user', '-u', action='store', default=os.environ.get("USER"), metavar='SSH_USER', help='dnsmasq server execute ssh account name')
parser.add_argument('--ssh-key', '-i', action='store', metavar='SSH_PRIVATE_KEY', help='dnsmasq server execute ssh key')
parser.add_argument('--remote-command-timeout', '-t', type=int, action='store', metavar='REMOTE_COMMAND_TIMEOUT', default=REMOTE_COMMAND_TIMEOUT, help='remote dnsmasq server execution timeout seconds')
parser.add_argument('--delay', action='store', type=int, metavar='DELAY SECONDS', default=DELAY, help='check delay seconds')
parser.add_argument('--dnsmasq-lease', action='store', metavar='DNSMASQ_DHCP_LEASE', default=DNSMASQ_DHCP_LEASE, help='local dnsmasq dhcp server lease file')
parser.add_argument('--dnsmasq-ddns-hosts', action='store', metavar='DNSMASQ_DDNS_HOSTS', default=DNSMASQ_DDNS_HOSTS, help='dnsmasq dns server dynamic dns hosts file')



def checksum_file(lease_file):
    m = hashlib.md5()
    with open(lease_file) as f:
        m.update(f.read().encode("utf-8"))
        
    return m.hexdigest()

def make_ddns_hosts_string(dnsmasq_lease):

    lines = []
    hostnames = []
    with open(dnsmasq_lease) as f:
        for line in f:
            #timestamp, macaddr, ipv4, hostname, ipv6 
            fields = re.split('\s+', line)
            if fields[3] == "*":
                continue
            if fields[3] in hostnames:
                continue
            lines.append("{0} {1}".format(fields[2], fields[3]))
            hostnames.append(fields[3])
            #lines.append([fields[2], fields[3]])

    #sorted(lines, key=lambda x:x[0])
    lines.sort()
    return "\n".join(lines) + "\n"


def make_ssh_command(server, args, remote_command=None):
    ssh_cmds = [SSH_CMD]
    ssh_cmds.extend(SSH_OPTIONS)
    ssh_cmds.append("-l")
    ssh_cmds.append(shlex.quote(args.ssh_user))
    if args.ssh_key:
        ssh_cmds.append("-i")
        ssh_cmds.append(shlex.quote(args.ssh_key))

    ssh_cmds.append(server)
    ssh_cmds.append(remote_command)
    return ssh_cmds


def main():
    args = parser.parse_args()
    before_checksum = ""
    while True:
        after_checksum = checksum_file(args.dnsmasq_lease)

        if before_checksum == after_checksum:
            print("{0}(md5sum:{1}) is not updated. skip".format(args.dnsmasq_lease, after_checksum))
            continue

        print("{0}(md5sum:{1}) is updated. execute dnsmasq servers hosts change".format(args.dnsmasq_lease, after_checksum))
        for server in args.servers:

            ddns_hosts_string = make_ddns_hosts_string(args.dnsmasq_lease)
            ssh_cmds = make_ssh_command(server, args, REMOTE_DNSMASQ_UPDATE_DDNS_COMMAND.format(shlex.quote(args.dnsmasq_ddns_hosts)))
            p = Popen(ssh_cmds, universal_newlines=True, stdin=PIPE, stderr=STDOUT)
            outs, errs = p.communicate(input=ddns_hosts_string, timeout=args.remote_command_timeout)
            if p.returncode != 0:
                sys.exit("ddns update failure. returncode:{0} message:{1}".format(p.returncode, errs))
            print("{0}: ddns update. returncode:{1}".format(server, p.returncode))

            ssh_cmds = make_ssh_command(server, args, REMOTE_DNSMASQ_RESTART_COMMAND)
            p = Popen(ssh_cmds, universal_newlines=True, stdin=PIPE, stderr=STDOUT)
            outs, errs = p.communicate(timeout=args.remote_command_timeout)
            print("{0}: restart dnsmasq. returncode:{1}".format(server, p.returncode))
            if p.returncode != 0:
                sys.exit("ddns update failure. returncode:{0} message:{1}".format(p.returncode, errs))

        before_checksum = after_checksum

        if args.oneshot:
            print("break loop")
            break

        time.sleep(args.delay)

if __name__ == "__main__":
    main()
