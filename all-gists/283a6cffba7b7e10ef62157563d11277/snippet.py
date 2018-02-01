from sys import*
o=ord
g=lambda s:print(''.join(map(lambda c:((c,chr(o(c)+65248))[o(c)<127],"　")[c==" "],s)))
if len(argv)>1:g(' '.join(argv[1:]))
else:
 while 1:g(input())