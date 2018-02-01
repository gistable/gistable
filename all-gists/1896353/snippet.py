from random import random
print "Pi:", sum(1 for i in range(2000000) if (random()**2 + random()**2) < 1)/2000000.0 * 4