#!/usr/bin/python

'''
Python-based gift exchange randomizer. 
Step through a list of people and, for each member of that list, 
select someone else to be a recipient of their gift. That recipient:
    
    A) Must not be themselves (no self-gifting)
    B) Must not already have been assigned as a recipient
    
'''

import random

# Participants
people = ['John','Jamie','Avis','Jim','Amy','Scot']

# Empty list to store the people who've already had an assigment made
assigned = []


# For each person, assemble a list of possible recipients.
for p in people:

    # Init a list to store potential recipients in
    recips = []
    
    # Remove already assigned people from potential recipients
    recips = list(set(people) - set(assigned))

    # Don't let a user give to themselves
    try:
        recips.remove(p)
    except:
        pass
            
    # Now grab a random person from the remaining recipients
    rand = random.randint(0, (len(recips))-1)
    randomRecip = recips[rand]
    
    # Assign that recipient to the "assigned" list so they don't appear again
    assigned.append(randomRecip)

    print "%s gives to %s" % (p, randomRecip)
    print
    

    
