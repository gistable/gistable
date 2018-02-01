import sys
import os
import xml.etree.ElementTree as ET
import logging
import re
from shutil import copyfile
from optparse import OptionParser

### This file came from the https://github.com/flow123d/flow123d repo they were nice enough to spend time to write this. 
### It is copied here for other people to use on its own.

# parse arguments
newline = 10*'\t';
parser = OptionParser(usage="%prog [options] [file1 file2 ... filen]", version="%prog 1.0",
    epilog = "If no files are specified all xml files in current directory will be selected. \n" +
             "Useful when there is not known precise file name only location")

parser.add_option("-o", "--output",     dest="filename",    default="coverage-merged.xml",
    help="output file xml name", metavar="FILE")
parser.add_option("-p", "--path",       dest="path",        default="./",
    help="xml location, default current directory", metavar="FILE")
parser.add_option("-l", "--log",        dest="loglevel",    default="DEBUG",
    help="Log level DEBUG, INFO, WARNING, ERROR, CRITICAL")
parser.add_option("-f", "--filteronly", dest="filteronly",  default=False, action='store_true',
    help="If set all files will be filtered by keep rules otherwise "+
		 "all given files will be merged and filtered.")
parser.add_option("-s", "--suffix",     dest="suffix",      default='',
    help="Additional suffix which will be added to filtered files so they original files can be preserved")
parser.add_option("-k", "--keep",       dest="packagefilters", default=None,  metavar="NAME", action="append",
    help="preserves only specific packages. e.g.: " + newline + 
         "'python merge.py -k src.la.*'" + newline + 
         "will keep all packgages in folder " +
         "src/la/ and all subfolders of this folders. " + newline +
         "There can be mutiple rules e.g.:" + newline + 
         "'python merge.py -k src.la.* -k unit_tests.la.'" + newline +
         "Format of the rule is simple dot (.) separated names with wildcard (*) allowed, e.g: " + newline +
         "package.subpackage.*")
(options, args) = parser.parse_args()


# get arguments
path = options.path
xmlfiles = args
loglevel = getattr(logging, options.loglevel.upper())
finalxml = os.path.join (path, options.filename)
filteronly = options.filteronly
filtersuffix = options.suffix
packagefilters = options.packagefilters
logging.basicConfig (level=loglevel, format='%(levelname)s %(asctime)s: %(message)s', datefmt='%x %X')



if not xmlfiles:
	for filename in os.listdir (path):
	    if not filename.endswith ('.xml'): continue
	    fullname = os.path.join (path, filename)
	    if fullname == finalxml: continue
	    xmlfiles.append (fullname)

	if not xmlfiles:
		print 'No xml files found!'
		sys.exit (1)

else:
	xmlfiles=[path+filename for filename in xmlfiles]



# constants
PACKAGES_LIST = 'packages/package';
PACKAGES_ROOT = 'packages'
CLASSES_LIST = 'classes/class';
CLASSES_ROOT = 'classes'
METHODS_LIST = 'methods/method';
METHODS_ROOT = 'methods'
LINES_LIST = 'lines/line';
LINES_ROOT = 'lines'



def merge_xml (xmlfile1, xmlfile2, outputfile):
	# parse
	xml1 = ET.parse(xmlfile1)
	xml2 = ET.parse(xmlfile2)

	# get packages
	packages1 = filter_xml(xml1)
	packages2 = filter_xml(xml2)

	# find root
	packages1root = xml1.find(PACKAGES_ROOT)


	# merge packages
	merge (packages1root, packages1, packages2, 'name', merge_packages);

	# write result to output file
	xml1.write (outputfile,  encoding="UTF-8", xml_declaration=True)


def filter_xml (xmlfile):
	xmlroot = xmlfile.getroot()
	packageroot = xmlfile.find(PACKAGES_ROOT)
	packages = xmlroot.findall (PACKAGES_LIST)

	# delete nodes from tree AND from list
	included = []
	if packagefilters: logging.debug ('excluding packages:')
	for pckg in packages:
		name = pckg.get('name')
		if not include_package (name):
			logging.debug ('excluding package "{0}"'.format(name))
			packageroot.remove (pckg)
		else:
			included.append (pckg)
	return included


def prepare_packagefilters ():
	if not packagefilters:
		return None

	# create simple regexp from given filter
	for i in range (len (packagefilters)):
		packagefilters[i] = '^' + packagefilters[i].replace ('.', '\.').replace ('*', '.*') + '$'



def include_package (name):
	if not packagefilters:
		return True

	for packagefilter in packagefilters:
		if re.search(packagefilter, name):
			return True
	return False

def get_attributes_chain (obj, attrs):
	"""Return a joined arguments of object based on given arguments"""

	if type(attrs) is list:
		result = ''
		for attr in attrs:
			result += obj.attrib[attr]
		return result
	else:
		return 	obj.attrib[attrs]


def merge (root, list1, list2, attr, merge_function):
	""" Groups given lists based on group attributes. Process of merging items with same key is handled by
		passed merge_function. Returns list1. """
	for item2 in list2:
		found = False
		for item1 in list1:
			if get_attributes_chain(item1, attr) == get_attributes_chain(item2, attr):
				item1 = merge_function (item1, item2)
				found = True
				break
		if found:
			continue
		else:
			root.append(item2)


def merge_packages (package1, package2):
	"""Merges two packages. Returns package1."""
	classes1 = package1.findall (CLASSES_LIST);
	classes2 = package2.findall (CLASSES_LIST);
	if classes1 or classes2:
		merge (package1.find (CLASSES_ROOT), classes1, classes2, ['filename','name'], merge_classes);

	return package1


def merge_classes (class1, class2):
	"""Merges two classes. Returns class1."""

	lines1 = class1.findall (LINES_LIST);
	lines2 = class2.findall (LINES_LIST);
	if lines1 or lines2:
		merge (class1.find (LINES_ROOT), lines1, lines2, 'number', merge_lines);

	methods1 = class1.findall (METHODS_LIST)
	methods2 = class2.findall (METHODS_LIST)
	if methods1 or methods2:
		merge (class1.find (METHODS_ROOT), methods1, methods2, 'name', merge_methods);

	return class1


def merge_methods (method1, method2):
	"""Merges two methods. Returns method1."""

	lines1 = method1.findall (LINES_LIST);
	lines2 = method2.findall (LINES_LIST);
	merge (method1.find (LINES_ROOT), lines1, lines2, 'number', merge_lines);


def merge_lines (line1, line2):
	"""Merges two lines by summing their hits. Returns line1."""

	# merge hits
	value = int (line1.get('hits')) + int (line2.get('hits'))
	line1.set ('hits', str(value))

	# merge conditionals
	con1 = line1.get('condition-coverage')
	con2 = line2.get('condition-coverage')
	if (con1 is not None and con2 is not None):
		con1value = int(con1.split('%')[0])
		con2value = int(con2.split('%')[0])
		# bigger coverage on second line, swap their conditionals
		if (con2value > con1value):
			line1.set ('condition-coverage', str(con2))
			line1.__setitem__(0, line2.__getitem__(0))

	return line1

# prepare filters
prepare_packagefilters ()


if filteronly:
	# filter all given files
	currfile = 1
	totalfiles = len (xmlfiles)
	for xmlfile in xmlfiles:
		xml = ET.parse(xmlfile)
		filter_xml(xml)
		logging.debug ('{1}/{2} filtering: {0}'.format (xmlfile, currfile, totalfiles))
		xml.write (xmlfile + filtersuffix,  encoding="UTF-8", xml_declaration=True)
		currfile += 1
else:
	# merge all given files
	totalfiles = len (xmlfiles)

	# special case if only one file was given
	# filter given file and save it
	if (totalfiles == 1):
		logging.warning ('Only one file given!')
		xmlfile = xmlfiles.pop(0)
		xml = ET.parse(xmlfile)
		filter_xml(xml)
		xml.write (finalxml,  encoding="UTF-8", xml_declaration=True)
		sys.exit (0)


	currfile = 1
	logging.debug ('{2}/{3} merging: {0} & {1}'.format (xmlfiles[0], xmlfiles[1], currfile, totalfiles-1))
	merge_xml (xmlfiles[0], xmlfiles[1], finalxml)


	currfile = 2
	for i in range (totalfiles-2):
		xmlfile = xmlfiles[i+2]
		logging.debug ('{2}/{3} merging: {0} & {1}'.format (finalxml, xmlfile, currfile, totalfiles-1))
		merge_xml (finalxml, xmlfile, finalxml)
		currfile += 1

