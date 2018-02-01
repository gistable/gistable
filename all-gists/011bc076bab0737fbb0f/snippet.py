# Spigot algorithm using Gosper's series for pi
# ref: section 6 of http://www.cs.ox.ac.uk/jeremy.gibbons/publications/spigot.pdf

from itertools import count
def div(a,b):
    return int(a/b)
# compose two 2x2 matrices
def comp(a,b):
    q,r,s,t = a
    u,v,w,x = b
    
    return (q*u+r*w, q*v+r*x, s*u+t*w, s*v+t*x)

def pi():
    state = (1,0,0,1)
    i = 1
    acc = 1
    while True:
        q,r,s,t = state
        print(i,q,r,s,t)
        
        # compute a digit
        x = 27*i-12
        y = div(q*x+5*r, s*x+5*t)
        
        # check y is safe
        x = 675*i-216
        if y==div(q*x+125*r,s*x+125*t):
            # yield the digit
            yield y
            #compute the new state
            state = comp((10,-10*y,0,1),state)
            
        else:
            # compute the next input
            j = 3*(3*acc+1)*(3*acc+2)
            x = (acc*(2*acc-1),j*(5*acc-2),0,j)
            acc += 1
            
            state = comp(state,x)
            i += 1
            
for a,b in zip(pi(),range(12)):
    print(a)