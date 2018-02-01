import datetime, sys

if len(sys.argv) != 3:
	print "usage: ", sys.argv[0], "<in> <out>"
	exit()

instr="00:01:57.640"
instr=sys.argv[1]

ints=datetime.datetime.strptime(instr, "%H:%M:%S.%f")
cutin=ints.hour*60*60*25 + ints.minute*60*25 + ints.second*25 + ints.microsecond*25/1000000.0
cutinseconds=ints.hour*60*60 + ints.minute*60 + ints.second + ints.microsecond/1000000.0

outstr="00:01:57.640"
outstr=sys.argv[2]

outts=datetime.datetime.strptime(outstr, "%H:%M:%S.%f")
cutout=outts.hour*60*60*25 + outts.minute*60*25 + outts.second*25 + outts.microsecond*25/1000000.0
cutoutseconds=outts.hour*60*60 + outts.minute*60 + outts.second + outts.microsecond/1000000.0
print "#in",instr,ints,"sec",cutinseconds
print "#out",outstr,outts,"sec",cutoutseconds
print "echo", int(cutin), ">inframe"
print "echo", int(cutout), ">outframe"

print "Record.Cutdiffseconds =", cutoutseconds-cutinseconds
print "Record.Cutinseconds =",   cutinseconds
print "Record.Cutoutseconds =",  cutoutseconds