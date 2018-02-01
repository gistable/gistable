############ All different probabilities, most general situation
import random

# Make sure these add up to 1
prob1 = .2  # 20%
prob2 = .45 # 45%
prob3 = .35 # 35%

r = random.random()

# If r is from 0 to .2
if r < prob1:
  # Random choice 1

# If r is from .2 to .65
else if r < prob1 + prob2:
  # Random choice 2
  
# If r is from .65 to 1.0
else if r < prob1 + prob2 + prob3:
  # Random choice 3
#################################################

############ If they're all equal probabilities
import random

# r will be one of these numbers, with equal probability
r = random.choice([0,1,2,3,4])

if r == 0:
  # Do stuff for 0
  
elif r == 1:
  # Do stuff for the 25% case
  
elif r == 2:
  # Do stuff for the 50% case
  
elif r == 3:
  # Do stuff for the 75% case
  
elif r == 4:
  # Do stuff for the 100% case
###########################################