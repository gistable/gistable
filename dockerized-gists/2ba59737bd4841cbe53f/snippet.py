import xml.etree.ElementTree as etree
import sys
import os.path

def visualize_xml(element, padding=' '):
	""" Visualize all ElementTree nodes by printing them to screen """

	if type(element.tag) != str:
		return

	output = padding[:-1] + "+-" + element.tag
	output = output.ljust(30)

	padding = padding + ' '

	val = ""
	if element.text and element.text.strip():
		val = "'%s' " % element.text.strip()

	attr = ", ".join(["@%s='%s'" % (k,v) for k,v in element.attrib.items()])

	print output, val, attr

	count = 0
	for child in element:
		count += 1
		#print padding + "|"
		if count == len(element):
			visualize_xml(child, padding + ' ')
		else:
			visualize_xml(child, padding + '|')

def main(filename):
	xml = etree.parse(filename)
	root = xml.getroot()
	visualize_xml(root)

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: python parse.py <filename.xml>"
		sys.exit(1)

	filename = sys.argv[1]
	if not os.path.exists(filename):
		print "Error: File does not exist", filename
		sys.exit(1)

	main(filename)
