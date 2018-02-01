#!/usr/bin/python3.2
# *-* coding: utf-8 *-*

# Ranger by seniorihor
# 02.03.2012 (c)

print('''Welcome on board, Captain!!!
Select a number of action:
     START  - "1" (if undefined - range from zero)
     FINISH - "2" (necessarily!)
     STEP   - "3" (how many numbers to pass)
...or you can combine it.
EXAMPLE: 2 or 12 or 1 2 3...
''')
q = input('Enter number of variants action: ')

# Check and define variable for argument of range
i = s = 0
while i < len(q):
  if   q[i] == '2':
    finish = int(input('Enter FINISH number: '))+1
    i+=1
  elif q[i] == '1' and len(q) > 1:
    start  = int(input('Enter START  number: '))
    i+=1
  elif q[i] == '3' and len(q) >= 3:
    step   = int(input('Enter STEP   number: '))
    i+=1
  elif q[i] == ' ' or q[i] == ',' or q[i] == '.' or q[i] == '-':
    i, s = i+1, s+1
  else:
    exit('ERROR: Bad numbers or you don\'t defined FINISH!')

p = i-s
if p > 3:
  exit('ERROR: More numbers!')

# Check and start execute range
if   p == 1:
  for i in range(finish):
    print(i, end=' ')
elif p == 2:
  for i in range(start, finish):
    print(i, end=' ')
elif p == 3:
  for i in range(start, finish, step):
    print(i, end=' ')
print()