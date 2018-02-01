"""
TotC_random_draw.py
An emulator of the random draw process from
Trial of the Clones by Zach Weinersmith
process in the book is to flip to a random page
and using the number in the corner for game
mechanics.
call it like this: 
>python TotC_random_draw.py [number of draws]
then it prints the outcome[s]
defaults to one roll. 
inspired to solve my own bug report from 
http://www.kickstarter.com/projects/999790007/trial-of-the-clone-a-choosable-path-gamebook-by-za/comments
"""
import sys
from random import sample

if len(sys.argv) == 2:
    num_rolls = int(sys.argv[1])
else:
    num_rolls = 1

possible_outcomes = [3]*53 + [2]*67 + [1]*71 + [0]*56

#we do each sample independently to emulated the page flip
#every random draw comes from the full set
for _ in xrange(num_rolls):
    print sample(possible_outcomes,1)[0]