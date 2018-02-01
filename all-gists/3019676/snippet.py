import sys
import time
import multiprocessing
import subprocess
import os.path

path = os.path.dirname(sys.argv[0])

def convert(arg):
	global path
	basename=os.path.splitext(os.path.basename(arg))
	dest="g:\\Stuff\%s.mp4" % (basename[0])
	cmd='%s\\ffmpeg.exe -i "%s" -f mp4 -vcodec copy -acodec libfaac -b:a 112k -ac 2 -y "%s"' % (path, arg, dest)
	print cmd
	return subprocess.call(cmd, shell=False)



if __name__ == '__main__':
	#count = multiprocessing.cpu_count()   
	count = 4
    	pool = multiprocessing.Pool(processes=count)
	print pool.map(convert, sys.arg