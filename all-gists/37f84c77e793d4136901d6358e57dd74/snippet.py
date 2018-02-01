import sys
import math

index = 0

# Example Input
# Begin
# + + 2277 * 3967 2 * / -185495049 -6989 - 33363302 33363301
# End
# Result: 36752

# Notes: The input must finish with "# End"

def polish(lex):
    global index
    if lex[index] == '+':
        index += 1
        return polish(lex) + polish(lex)
    if lex[index] == '-':
        index += 1
        return polish(lex) - polish(lex)
    if lex[index] == '*':
        index += 1
        return polish(lex) * polish(lex)
    if lex[index] == '/':
        index += 1
        return polish(lex) // polish(lex)
    if lex[index] == '%':
        index += 1
        return polish(lex) % polish(lex)

    index += 1
    return int(lex[index-1])


concat = []
for lines in sys.stdin:
    lex = lines.split()
    b = False
    for word in lex:
        if word == "#":
            b = True
        if word == "End":
            print(math.floor(polish(concat)))
            index = 0
            concat = []
    if b == False:
        concat = concat + lex

    print(lines)