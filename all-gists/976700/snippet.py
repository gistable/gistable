import os
import subprocess

test_cmd = 'netcat -vz 193.1.172.59 75-85'
expected = 'vega.ucd.ie [193.1.172.59] 80 (http) open'

process = subprocess.Popen(test_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
err = process.stderr.read()
print str(err)
