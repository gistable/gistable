import subprocess, sys
from datetime import datetime
from time import sleep

timestamp = lambda : datetime.now().isoformat()

# # pager_rtl.sh --
# rtl_fm -M fm -f 152.48M -r22050 -s88200 -g 42 -l 30 

rtl_fm = subprocess.Popen("./pager_rtl.sh",
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        shell=True)

#rtl_fm.poll()
#sleep(5)

# # pager_ng.sh --
# multimon-ng -t raw -f alpha -a POCSAG512 -

multimon_ng = subprocess.Popen("./pager_ng.sh",
        stdin=rtl_fm.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True)


# try / catch hack for ctrl+c, 
# there's probably a better way to ensure process stop when finished
try:
        while True:
                nextline = multimon_ng.stdout.readline()
                multimon_ng.poll()
                if nextline.__contains__("Alpha:"):    # filter out only the alpha
                        nextline = nextline.split('POCSAG512: Alpha: ')[1]
                        sys.stdout.write(timestamp() + " " + nextline)
                        sys.stdout.flush()
except:
        pass


rtl_fm.kill() 
multimon_ng.kill()
