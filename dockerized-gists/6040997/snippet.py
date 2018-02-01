import subprocess
import re
def rmAll():
	output = subprocess.check_output("git status", shell=True)
	matches = re.findall('deleted:    .*', output)
	for n in matches:
		clean = n.replace("deleted:    ","")
		subprocess.call("git rm "+clean, shell=True)
