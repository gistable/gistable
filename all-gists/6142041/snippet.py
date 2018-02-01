#!/usr/bin/python
import urllib2, re,sys
a=''
if len(sys.argv) == 2:
        a=sys.argv[1]
else:
        a=raw_input("Enter the url :")
req = urllib2.Request(a)
resp = urllib2.urlopen(req)
html = resp.read()
def indent(a):
        a=a.group(0)
        if a=='{':
                return "\n"+a
        elif a=='}' or a==';':
                return a+"\n"
html=re.sub("[{};]",indent,html)
count=0
Html=''
html=html.split('\n')
for i in html:
 try:
        if i[0] =='{':
                count+=1
        Html+="\n"+' '*count+i
        if i[-1]=='}':
                count-=1
 except:
        pass
open(a.split('/')[-1],'w+').write(Html)
print 'The js file is stored with proper indentation in \'  %s  \'\nhere are the json links' %a.split('/')[-1]
for i in set(re.findall("\"http:[^;\]{}]*\.json\"", ''.join(html))):
        print i
