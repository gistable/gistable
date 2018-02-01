# author: Aaditya Prakash

# NVIDIA-SMI does not show the full command, and when it was launched and its RAM usage.
# PS does but it does but you need PIDs for that
# lsof /dev/nvidia gives PIDs but only for the user invoking it

# usage:
#        python programs_on_gpu.py

# Sample Output
#GPU_ID     GPU_MEM    USER       PGRP       PID        %CPU       %MEM       STARTED    TIME       COMMAND
#-----      -------    ----       ----       ---        ----       ----       -------    ----       -------
#1          11738MiB   ap         25640      25640      158        2.4        00:47:15   00:43:01   python     train.py
#2          11843MiB   ap         23806      23806      99.4       2.0        00:46:22   00:27:50   python     cifar10_cnn.py
#3          11841MiB   ap         14518      14518      0.1        2.0        22:07:52   00:00:12   /usr/bin/python /usr/local/bin/ipython

#        python programs_on_gpu.py --less_info

# Sample Output
#USER      PGRP   PID %CPU %MEM  STARTED     TIME COMMAND
#ap       25640 25640  158  2.4 00:47:15 00:43:12 python train.py
#ap       23806 23806 99.4  2.0 00:46:22 00:27:57 python cifar10_cnn.py
#ap       14518 14518  0.1  2.0 22:07:52 00:00:12 /usr/bin/python /usr/local/bin/ipython



import os
import sys
import subprocess
import itertools

LESS_INFO = False
if len(sys.argv) == 2:
    LESS_INFO = bool(sys.argv[1])

nvidia = subprocess.Popen(["nvidia-smi"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
out= nvidia.communicate()[0].splitlines()[::-1]

selected_lines = list(itertools.takewhile(lambda i: not i.startswith('|=='), out))[1:]

pid_data = {}
for line in selected_lines:
    try:
        _, gpuid, pid, _, language, gpu_memory, _ = line.split()
    except:
        print "NO programs running on GPU"
        sys.exit(1)
    pid_data[pid] = [gpuid, gpu_memory]

if LESS_INFO:
    os.system("ps f -o user,pgrp,pid,pcpu,pmem,start,time,command -p " + ' '.join(pid_data.keys()))
    sys.exit(1)

ps_command = "ps f -o user,pgrp,pid,pcpu,pmem,start,time,command -p " + ' '.join(pid_data.keys())
header     = "GPU_ID GPU_MEM USER PGRP PID %CPU %MEM STARTED TIME COMMAND".split()
header_line= "----- -------  ---- ---- --- ---- ---- ------- ---- -------".split()


ps = subprocess.Popen(ps_command.split(), stdout=subprocess.PIPE, stdin=subprocess.PIPE)
out_ps = ps.communicate()[0].splitlines()[1:]

data = []
for line in out_ps:
    line_data = line.split()
    nv_data = pid_data[line_data[2]]
    data.append(nv_data + line_data)


for h in header: print '{0: <10}'.format(h),
print ' '
for h in header_line: print '{0: <10}'.format(h),
print ' '

for data_item in data:
    for d in data_item: print '{0: <10}'.format(d),
    print ''