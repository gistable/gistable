#!/usr/bin/python

import argparse, os, subprocess


# Grab the script directory to use as default
current_directory = os.path.dirname(os.path.abspath(__file__))

def parse_cli_arguments():
	parser = argparse.ArgumentParser(description = 'Grabs all DNG files from the connected Android device\'s camera roll.')
	parser.add_argument('--output-path', type = str, help = 'The path to download the DNGs to. Default: {script_path}/raw', 
		default = os.path.join(current_directory, 'raw'))
	parser.add_argument('-o', '--overwrite', help = 'If set, overwrites any existing file. Default: don\'t overwrite')
	
	return parser.parse_args()

args = parse_cli_arguments()



print "Listing files on your device..."
proc = subprocess.Popen(['adb', 'shell', 'ls', '/sdcard/DCIM/Camera/'], stdout=subprocess.PIPE)
proc.wait()

print "Downloading DNGs..."

output_path = args.output_path
if not os.path.exists(output_path):
    os.makedirs(output_path)

overwrite = args.overwrite

while True:
  line = proc.stdout.readline()
  if line != '':
    line = line.rstrip()
    if (line.endswith(".dng")): 
    	source_path = "/sdcard/DCIM/Camera/{filename}".format(filename = line)
    	dest_path = os.path.join(output_path, line)

    	if overwrite or not os.path.exists(dest_path):
    		subprocess.call(['adb', 'pull', source_path, dest_path])
  else:
    break

print "Done!"