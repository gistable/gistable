 def randomvariate(pdf,n=1000,xmin=0,xmax=1):  
  """  
 Rejection method for random number generation  
 ===============================================  
 Uses the rejection method for generating random numbers derived from an arbitrary   
 probability distribution. For reference, see Bevington's book, page 84. Based on  
 rejection*.py.  
   
 Usage:  
 >>> randomvariate(P,N,xmin,xmax)  
  where  
  P : probability distribution function from which you want to generate random numbers  
  N : desired number of random values  
  xmin,xmax : range of random numbers desired  
    
 Returns:   
  the sequence (ran,ntrials) where  
   ran : array of shape N with the random variates that follow the input P  
   ntrials : number of trials the code needed to achieve N  
   
 Here is the algorithm:  
 - generate x' in the desired range  
 - generate y' between Pmin and Pmax (Pmax is the maximal value of your pdf)  
 - if y'<P(x') accept x', otherwise reject  
 - repeat until desired number is achieved  
   
 Rodrigo Nemmen  
 Nov. 2011  
  """  
  # Calculates the minimal and maximum values of the PDF in the desired  
  # interval. The rejection method needs these values in order to work  
  # properly.  
  x=numpy.linspace(xmin,xmax,1000)  
  y=pdf(x)  
  pmin=0.  
  pmax=y.max()  
   
  # Counters  
  naccept=0  
  ntrial=0  
   
  # Keeps generating numbers until we achieve the desired n  
  ran=[] # output list of random numbers  
  while naccept<n:  
  x=numpy.random.uniform(xmin,xmax) # x'  
  y=numpy.random.uniform(pmin,pmax) # y'  
   
  if y<pdf(x):  
   ran.append(x)  
   naccept=naccept+1  
  ntrial=ntrial+1  
    
  ran=numpy.asarray(ran)  
    
  return ran,ntrial  