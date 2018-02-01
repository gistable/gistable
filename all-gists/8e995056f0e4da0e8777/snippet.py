import xml.etree.ElementTree as ET
tree = ET.parse(sys.argv[1])
root = tree.getroot()

for svc in tree.iter(tag='service'):
  if svc.attrib.has_key('product'):
		product = svc.attrib['product'].rstrip()
	else:
		continue

	if svc.attrib.has_key('version'):
		version = svc.attrib['version'].rstrip()
	else:
		version = "[VERSION]"

	if svc.attrib.has_key('ostype'):
		ostype = svc.attrib['ostype'].rstrip()
	else:
		ostype = "[OS]"

	print "%s %s %s" % (product, version, ostype)
