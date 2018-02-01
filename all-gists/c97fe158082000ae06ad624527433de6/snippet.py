from itertools import permutations, product, zip_longest
from sys import argv

args = sum([[1, 11] if arg in "aA" else [int(arg)] for arg in argv[1:5]], [])

for xs in permutations(args, 4):
    if sum(n == 1 or n == 11 for n in xs) > len(args) - 4:
        continue
    for ops in product("+-*/", repeat=3):
        for exp in ["(...).(...)", "((...)..)..", "(..(...)).."]:
            exp = exp.replace(".", "{}").format(*sum(zip_longest(xs, ops), ()))
            try: 
                if eval(exp) == 24:
                    print(exp)
                    exit()
            except ZeroDivisionError:
                pass

print("No solution")