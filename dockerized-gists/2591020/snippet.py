'''
Warning! Your mileage may vary 

Based on:

- Read this for EC2 setup info and the approach - http://www.dikant.de/2010/10/08/setting-up-a-vpn-server-on-amazon-ec2/
- https://gist.github.com/1130401
- EC2 fabric bits via - https://github.com/slacy/fabric-ec2

'''

import boto
import re

from fabric.api import *
from fabric.contrib import files


env.user = 'ubuntu'
# change this...
env.key_filename = '/Users/your-username-here/.ssh/gsg-keypair.pem'

# and these...
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
VPN_USER = ''
VPN_PASS = ''


def get_all_machines():
    ec2_conn = boto.connect_ec2(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    reservations = ec2_conn.get_all_instances()
    all_machines = []
    for reservation in reservations:
        all_machines += reservation.instances
    return all_machines


def machine_roles(role):
    machines = get_all_machines()
    matches = []
    for mach in machines:
        roles = re.split('[, ]+', mach.tags['role'])
        if role in roles:
            matches.append(mach)
    return matches


def _init_roles():
    ec2_machines = get_all_machines()

    for mach in ec2_machines:
        print mach
        roles = re.split('[, ]+', mach.tags.get('role', ''))
        for r in roles:
            if r not in env.roledefs:
                env.roledefs[r] = []
            if mach.public_dns_name:
                env.roledefs[r].append(mach.public_dns_name)

        ec2_dns = [mach.public_dns_name for mach in ec2_machines]
        print "ec2_dns: %s" % ec2_dns

    print "roledefs: %s" % env.roledefs


@roles('ubuntu')
def dist_upgrade():
    sudo('apt-get -qy update')
    sudo('apt-get -qy dist-upgrade')


@roles('ubuntu')
def install_vpn():
    sudo('apt-get -qy install pptpd')

    files.append('/etc/pptpd.conf', 'localip 192.168.240.1', use_sudo=True)
    files.append('/etc/pptpd.conf', 'remoteip 192.168.240.2-102', use_sudo=True)

    files.append('/etc/ppp/pptpd-options', 'ms-dns 8.8.8.8', use_sudo=True)
    files.append('/etc/ppp/pptpd-options', 'ms-dns 8.8.4.4', use_sudo=True)

    files.append('/etc/ppp/chap-secrets', '%(username)s pptpd %(password)s *' % ({
            'username': VPN_USER,
            'password': VPN_PASS,
        }),
        use_sudo=True)

    sudo('/etc/init.d/pptpd restart')

    files.uncomment('/etc/sysctl.conf', 'net\.ipv4\.ip_forward=1', use_sudo=True)

    sudo('sysctl -p')
    sudo('iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE')

    if not files.contains('/etc/rc.local', 'iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE', use_sudo=True):
        files.comment('/etc/rc.local', 'exit 0', use_sudo=True)
        files.append('/etc/rc.local', 'iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE', use_sudo=True)
        files.append('/etc/rc.local', 'exit 0', use_sudo=True)

_init_roles()
