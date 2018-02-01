import re 
f = open("1.in", "r")
N = int(f.readline())
a = 26
for i in range(N):
   mydict = {}
   total = 0
   input = f.readline()
   input = re.sub('[^A-Za-z0-9]+', '', input)
   input = input.lower()
   for ii in range(len(input)):
     mydict[input[ii]] = 0
   for ii in range(len(input)):
     mydict[input[ii]] = mydict[input[ii]] + 1
   mydictsorted = sorted(mydict.items(), key=lambda x: x[1], reverse = True)
   mm = 0
   for m in mydictsorted:
     total = total + (a-mm)*m[1]     
     mm = mm + 1
   print "Case #"+str(i+1)+": "+str(total)