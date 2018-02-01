# -*- coding: utf-8 -*- 

from os import walk, sep
from os.path import basename, isdir
from sys import argv

def tree(startpath, print_files=False):
  for root, subdirs, files in walk(startpath):
		level = root.replace(startpath, '').count(sep)
		indent = '  |' * (level-1) + '  +- '
		print "%s%s/" % (indent, basename(root))
		#print "{}{}/".format(indent, os.path.basename(root))
		subindent = '  |' * (level) + '  +- '
		if print_files:
			for f in files:
				print "%s%s" % (subindent, f)
				#print "{}{}/".format(subindent, f)

def usage():
	return '''Usage: %s [-h] [-f] [PATH]
Print tree structure.
Options:
-h, --help	Print help info
-f			Print files as well as directories
PATH		Path to process''' % basename(argv[0])

def main():
	path = '.'

	# Check for help
	if ('-h' or '--help') in argv:
		print usage()
	# tree
	elif len(argv) == 1:
		tree(path)
	# tree -f
	elif len(argv) == 2 and argv[1] == '-f':
		tree(path, True)
	# tree dir
	elif len(argv) == 2:
		path = argv[1]
		if isdir(path):
			tree(path)
		else:
			print 'ERROR: \'' + path + '\' is not a directory'
	# tree -f dir
	elif len(argv) == 3 and argv[1] == '-f':
		path = argv[2]
		if isdir(path):
			tree(path, True)
		else:
			print 'ERROR: \'' + path + '\' is not a directory'
	else:
		print 'ERROR: Wrong parameters'
		print usage()


if __name__ == '__main__':
	main()
