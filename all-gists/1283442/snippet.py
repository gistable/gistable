# from https://libbits.wordpress.com/2011/04/09/get-total-rsync-progress-using-python/

import subprocess
import re
import sys

print('Dry run:')
cmd = 'rsync -az --stats --dry-run ' + sys.argv[1] + ' ' + sys.argv[2]
proc = subprocess.Popen(cmd,
  shell=True,
  stdin=subprocess.PIPE,
  stdout=subprocess.PIPE,
  )
remainder = proc.communicate()[0]
mn = re.findall(r'Number of files: (\d+)', remainder)
total_files = int(mn[0])
print('Number of files: ' + str(total_files))

print('Real rsync:')
cmd = 'rsync -avz  --progress ' + sys.argv[1] + ' ' + sys.argv[2]
proc = subprocess.Popen(cmd,
  shell=True,
  stdin=subprocess.PIPE,
  stdout=subprocess.PIPE,
)
while True:
  output = proc.stdout.readline()
  if 'to-check' in output:
    m = re.findall(r'to-check=(\d+)/(\d+)', output)
    progress = (100 * (int(m[0][1]) - int(m[0][0]))) / total_files
    sys.stdout.write('\rDone: ' + str(progress) + '%')
    sys.stdout.flush()
    if int(m[0][0]) == 0:
      break

print('\rFinished')
