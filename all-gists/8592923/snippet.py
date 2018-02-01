#!/usr/bin/python
#Compiles CUDA file and displays Kernel memory requirements in a table
import sys
import subprocess
def startpos(line):
	found=0;
	val=0;
	for each in line:
		if(found==0 and (each in "1234567890")):
			found=1
		if(found==1 and (each not in "1234567890")):
			return val
		val=val+1
	return val
print "Kernel Memory Analysis"
filename=""
if len(sys.argv)>1:
	for each in sys.argv:
		if ".cu" in each:
			filename=each;
	if filename=="":
		print "filename.cu missing"
		exit()
else:
	print "Usage: ",sys.argv[0]," filename.cu"
	exit()
print '\033[1m'+'{0: <48}'.format("Function")," reg\tsmem\t   cmem"+'\033[0m'
print "________________________________________________________________________________"
# '-c', '-o', '__meminfo_temp.o', 
p = subprocess.Popen(['nvcc', filename, '-arch=sm_21', '--ptxas-options=-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()
valueprinted=1
for line in err.split('\n'):
	if(line.find("ptxas info    : Function properties for")!=-1):
		line=line.replace("ptxas info    : Function properties for ","").replace("_Z","").split("N7")[0]
		if(valueprinted==0):
			print ""
		valueprinted=0
		print '{0: <50}'.format(line[startpos(line):50]),
	if(line.find("ptxas info    : Used ")!=-1):
		line=line.replace("ptxas info    : Used ","")
		line=line.split(",")
		reg=0; smem=0; cmem=""; 
		for each in line:
			if(each.find("registers")!=-1):
				reg =int(each.replace("registers",""))
			elif(each.find("smem")!=-1):
				smem=int(each.replace(" bytes smem",""))
			elif(each.find("cmem")!=-1):
				cmem=cmem+" "+'{0: >7}'.format(each.replace(" bytes cmem",""))
			else:
				pass#print each
		print reg,"\t",
		if(smem!=0):
			print smem,"\t",
		else:
			print "\t",
		print cmem
		#print line
		valueprinted=1
#p = subprocess.Popen(['rm', '__meminfo_temp.o'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
