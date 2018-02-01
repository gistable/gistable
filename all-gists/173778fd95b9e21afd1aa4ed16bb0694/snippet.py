#!/usr/bin/env python3
from securitycenter import SecurityCenter5
import subprocess

def vulns():
 sc = SecurityCenter5('nessus')
 sc.login('nessusapi', 'Afinepassword!')
 response = sc.get('status')
 hosts = sc.analysis(tool='sumip', page=0, page_size=10, sortDir='desc',sortField='score')

 print('\n')
 print("[Top 10 Vulnerable Hosts]")
 print('\n')

 for v in hosts:
   print('-' * 50)
   print('IP: ' + v['ip'])
   print('DNS: ' + v['dnsName'])
   print('OS: ' + v['osCPE'])
   print('Critical Vulenrablities: ' + v['severityCritical'])
   print('High Vulnerabilities ' + v['severityHigh'])
   print('Medium Vulnerabilities ' + v['severityMedium'])
   print('-' * 50)
   print('\n')
   
 sc.logout
 
vulns()