import re
import os
 
String = "ABRACADABRA"
pat = "DA"
pat1 = pat
if len(String) < len(pat):
    print "Enter Correct Pattern"
 
for i in range(0,(len(String)-len(pat))+1):
    print "iteration "+str(i)
    print String
    print pat1
    for k in range(0,len(pat)):
        if String[i] == pat[k]:
            i+=1
            flag = 1
        else:
            flag = 0
            break
 
    if flag == 1:
        print "match"
        break
    pat1 = ' ' + pat1
if flag == 0:
    print "No match"
 
 
 