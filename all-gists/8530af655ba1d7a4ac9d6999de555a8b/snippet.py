#!/usr/bin/env python
#
# Anton Todorov (a.todorov@storpool.com)
#
# add/change  <blockio /> element to the VM XML
#
# vmTweakDiskBlockioBlockSize.py <XMLfile>

from sys import argv
import syslog

dbg = 1

if dbg:
	syslog.openlog('vmTweakDiskBlockioBlockSize.py', syslog.LOG_PID)

try:
	import lxml.etree as ET
except ImportError:
	raise RuntimeError("lxml Python module not found! Install from distribution package or pip install lxml")

xmlFile = argv[1]

et = ET.parse(xmlFile, ET.XMLParser(strip_cdata=False,remove_blank_text=True))

# ugly but working
domain = et.getroot()[0].getparent()

vm_name = et.find(".//name").text

for disk in et.findall(".//disk"):
	if disk.get('device') == 'disk':
		if disk.get('type') == 'file':
			#<disk><target/>
			target_dev = ''
			for e in disk.findall(".//target"):
				target_dev = e.get('dev')
				if target_dev[0:2] == 'vd':
					#<target dev="vda" bus="virtio"/>
					e.set("bus","virtio")
			if target_dev[0:2] != 'vd':
				if dbg:
					syslog.syslog(syslog.LOG_INFO, "VM {0} not virtio-blk {1}".format(vm_name,target_dev))
				continue
			#<disk><driver/>
			for e in disk.findall(".//driver"):
				if e.get('type') == 'qcow2' and e.get("name") == 'qemu':
					if dbg:
						syslog.syslog(syslog.LOG_INFO, "VM {0} Setting blockio *_block_size on {1}".format(vm_name,target_dev))
					blockio = None
					for blockio in disk.findall(".//blockio"):
						if dbg:
							syslog.syslog(syslog.LOG_INFO, "VM {0} ${1} already have blockio".format(vm_name,target_dev))
					if blockio == None:
						blockio = ET.Element("blockio")
					blockio.set("logical_block_size", str(4096))
					blockio.set("physical_block_size", str(4096))
					disk.append(blockio)

et.write(xmlFile,pretty_print=True)
