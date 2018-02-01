import random, numpy

def genGuess(N,W,H):
    '''Generate sensible initial guess vector (random circle coordinates and radii)'''
    z=numpy.zeros(3*N)
    for i in xrange(0,N):
        z[i*3]=random.random()*W
        z[i*3+1]=random.random()*H
        z[i*3+2]=0.001*min(W,H)+random.random()*(0.009*min(W,H))
    return(z)

def getPairs(N):
    '''Generate all (2-way) unique pairings of N objects'''
    result=[]
    for i in xrange(0,N):
        for j in xrange(0,i):
            result.append([i,j])
    return(numpy.array(result))

def createObj(N,W,H):
    '''Function closure which initialises and creates a function for calculating the packing density of N circles in an W*H rectangle.  Circle coords and dimensions are represented by a single list z'''
    cpairs=getPairs(N)
    A=cpairs[:,0]
    B=cpairs[:,1]
    ind=range(0,3*N)
    a,b,c=ind[0:3*N:3],ind[1:3*N:3],ind[2:3*N:3]
    def newObj(z):
        '''Calculate packing density of N circles in W*H rectangle (N,W,H defined on function initialisation).  Circle coords and dimensions are represented by a single list z'''
        z=numpy.array(z,dtype=numpy.float)
        # Split z into x,y,r triplets: z[0],z[1],z[2] -> x1,y1,r1
        #x,y,r=z[a],z[b],z[c]
        x,y,r=z.take(a,axis=0),z.take(b,axis=0),z.take(c,axis=0)
        # Some linear inequality constraints to be satisfied
        c1=x+r-W # <0  
        c2=y+r-H # <0
        c3=r-x # <= 0
        c4=r-y # <=0
        # Many nonlinear inequality constraints
        #c5=r[A]+r[B]-numpy.sqrt((x[A]-x[B])**2+(y[A]-y[B])**2) # <=0
        c5=r.take(A,axis=0)+r.take(B,axis=0)-numpy.sqrt(numpy.power(x.take(A,axis=0)-x.take(B,axis=0),2)+numpy.power(y.take(A,axis=0)-y.take(B,axis=0),2)) # <=0

        c1=c1[c1>0]
        c2=c2[c2>0]
        c3=c3[c3>0]
        c4=c4[c4>0]
        c5=c5[c5>0]
        constraints=numpy.concatenate((c1,c2,c3,c4,c5))

        # Actual objective function (fraction of area covered)
        res=numpy.pi*numpy.sum(numpy.power(r,2))/(W*H)-numpy.sum(numpy.power(constraints,2))
        return(-1*res)
    return(newObj)

def vecToCircles(z):
    N=len(z)/3
    '''Convert z vector to an array of circle centres and radii'''
    ind=[x for x in xrange(0,3*N)]
    # Split z into x,y,r triplets: z[0],z[1],z[2] -> x1,y1,r1
    x,y,r=numpy.array([z[i] for i in ind[0:3*N:3]]),numpy.array([z[i] for i in ind[1:3*N:3]]),numpy.array([z[i] for i in ind[2:3*N:3]])
    clist=numpy.empty((N,3),numpy.float)
    clist[:,0],clist[:,1],clist[:,2]=x,y,r
    return(clist)

def drawCircle(x,y,r,s=2,fillcol="none",strokecol="black"):
    '''Draw a circle with centre x,y radius r, line thickness s, fill colour fillcol and line colour strokecol.'''
    return('''<circle cx="%s" cy="%s" r="%s" stroke-width="%s" fill="%s" stroke="%s"/>\n'''%(x,y,r-4*s/10,s,fillcol,strokecol))

def drawRect(x,y,w,h,s=2,fillcol="none",strokecol="black"):
    '''Draw a rectangle with top left corner x,y, width w, height h, line thickness s, fill colour fillcol, line colour strokecol, exploded slightly so inner edge is rectangle specified by 1st 4 params.'''
    return('''<rect x="%s" y="%s" width="%s" height="%s" stroke-width="%s" fill="%s" stroke="%s"/>\n'''%(x-s/2,y-s/2,w+s,h+s,s,fillcol,strokecol))

def svgHeader(w,h):
    '''Write valid svg header specifying bounding box w wide and h high'''
    string='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" version="1.1">\n'''%(w,h)
    return(string)

def svgFooter():
    '''Write svg footer'''
    return('</svg>')

# Demo script
if __name__ == "__main__":
    import time
    from scipy import optimize
    
    N=27            # Number of circles
    w,h=10,10       # Native rectangle dimensions
    rows,cols=12,12 # Graphical array size
    celldim=10      # Final graphics scaling factor
    margin=1        # Gap between plots (native scale).  Should be >= 2* line
    line=0.1        # Line thickness for graphics (native scale)

    # Generate a suitable objective function
    ObjFun=createObj(N,w,h)
    maxr=min(w,h)/2.0
    outf=open("BubblesOptArray100.svg","w") # Prepare to draw circles in .svg file
    outf.write(svgHeader(cols*w*(celldim+margin)+margin*celldim,rows*h*(celldim+margin)+margin*celldim))

    b=[(0,w),(0,h),(0.01*maxr,maxr)]*N

    for x in xrange(0,rows*cols):
        arrx=x%cols
        arry=x//rows
        print((arrx,arry))
        start=time.time()
        # Randomly generate a sensible starting guess
        z=genGuess(N,w,h)
        # Gradient based fmin_l_bfgs_b from scipy.optimize
        opt=optimize.fmin_l_bfgs_b(ObjFun,z,bounds=b,m=12,maxfun=500000,approx_grad=True)
        print("Optimisation time: "+str(time.time()-start))
        res=opt[0]
        print("Initial guess objective function: "+str(ObjFun(z)))
        print("Final, optimised objective function: "+str(ObjFun(res)))
        print(opt[2]['warnflag'])
        print(opt[2]['task'])
        print(opt[2]['funcalls'])
        # Draw resulting circles
        clist=vecToCircles(res*celldim)
        # Offset circles for array
        clist[:,0]=clist[:,0]+margin*celldim+arrx*(celldim+margin)*w
        clist[:,1]=clist[:,1]+margin*celldim+arry*(celldim+margin)*h
        for j in xrange(0,N):
            outf.write(drawCircle(clist[j,0],clist[j,1],clist[j,2],s=line*celldim))
        outf.write(drawRect(margin*celldim+arrx*(celldim+margin)*w,margin*celldim+arry*(celldim+margin)*h,w*celldim,h*celldim,s=line*celldim))
    outf.write(svgFooter())
    outf.close()
