



from __future__ import print_function, unicode_literals
"""
t=int(input())
k=int(input())
count =0
a=list ()
while count!=t:
    item=int(input())
    a.append(item)
    count+=1
"""


#a=[1,1,1,2,2,9,10] # test case runs well except others
a=[3,0,-5] # should be -1 yes
k=7

times = 0


if all(i>=k for i in a)==True: # base case
  print (times)
  
while any(i <k for i in a)==True and len(a)>1:
  a.sort()
  x=a[0]
  y=a[1]
  result= lambda x,y: 1*x + 2*y
  a=a[2:] # still work if empty list
  times+=1 
  a.append(result(x,y)) # forgot to add last value inside list
  if all(i>=k for i in a)==True:
    print(times)
    break# leave while loop if conditions are met
if any (i<k for i in a)==True: #base case
  print (-1)
  

  
  

    

  
    
  
  
  
    
  
  
  

    
