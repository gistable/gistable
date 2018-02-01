"""
Simple script I whipped up to dump MSN Messenger logs in XML to a readable 
plaintext format. It's not very robust, nor am I sure which versions of MSN
Messenger it's compatible or incompatible with; I just had a specific 
conversation I wanted to read, and this was the vehicle to that end.

By David Warde-Farley -- user AT cs dot toronto dot edu (user = dwf)
 
Redistributable under the terms of the 3-clause BSD license 
(see http://www.opensource.org/licenses/bsd-license.php for details)
"""

import sys
from xml.dom.minidom import parse

if len(sys.argv) != 2:
	print >>sys.stderr, "usage: " + sys.argv[0] + " <inputfile>"
	sys.exit(1)

doml = parse(sys.argv[1])
for message in doml.getElementsByTagName("Message"):
	fromNode = message.getElementsByTagName("From")[0]
	userNode = fromNode.getElementsByTagName("User")[0]
	name = userNode.getAttribute("FriendlyName") + \
		" says:"
	print name.encode('utf-8')
	msg = message.getElementsByTagName("Text")[0].firstChild.nodeValue
	print msg.encode('utf-8')
	print ""