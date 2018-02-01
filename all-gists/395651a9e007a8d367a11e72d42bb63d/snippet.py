import math
import timeit
a=int(raw_input("enter the number: "))
i=2
start = timeit.default_timer()
if a%2==0 and a!=2:
   print a,'is not a prime'
if a%3==0:
   print a,'is not a prime'
if a%5==0:
   print a,'is not a prime'
if a%7==0:
   print a,'is not a prime'
else:
   while i<=a//2:
      if a%i==0:
         print a,'is not a prime'
         i = a
      i = i + 1
   if i!=a+1:
      print a,'is a prime'
stop = timeit.default_timer()
print stop-start
