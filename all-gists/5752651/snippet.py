import os, time, subprocess

def run_command_silently(command):
    with open(os.devnull, 'wb') as devnull:
        subprocess.check_call(command.split(' '), stdout=devnull, stderr=subprocess.STDOUT)

run_command_silently('ping -c 1 255.255.255.255')
time.sleep(0.5)
arp_entries = subprocess.check_output(('arp','-na')).splitlines()
all_ip_and_macs = []

for entry in arp_entries:
    ip_addr, rest = entry.split('(')[1].split(') at ')
    mac_addr = rest.split(' on ')[0]
    all_ip_and_macs.append((ip_addr, mac_addr))

for ip_mac_tuple in all_ip_and_macs:
    print 'IP:', ip_mac_tuple[0], 'MAC:', ip_mac_tuple[1]