# WWW * GPU = PIXEL I/O
# X = 6
# O != 1
from itertools import permutations

for digits in permutations(d for d in range(10) if d != 6):
    W, G, P, U, I, E, L, O = digits[:8]
    if (O != 1 and O * (W*100+W*10+W) * (G*100+P*10+U) == (P*100000+I*10000+6000+E*100+L*10+I)):
        print ("{}{}{} * {}{}{} = {}{}6{}{} {}/{}".format(W, W, W, G, P, U, P, I, E, L, I, O))