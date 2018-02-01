import sys
t={}
def w(o):
 c=t
 for l in o:
  c[l]=c[l]if l in c else{}
  c=c[l]
 c[None]=None
g=lambda t,b,i:reduce(lambda i,l:i+[b]if l is None else g(t[l],b+l,i),t,i)
map(w,open(sys.argv[1]).read().split("\n"))
while 1:
 b=raw_input()
 print g(reduce(lambda c,l:c[l]if l in c else[],b,t),b,[])