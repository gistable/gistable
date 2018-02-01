# 3. Iterative/recursive log function
def myLog(x, b):
    a = 0
    while b ** a <= x:
        a += 1
    return a - 1

# 4. Interlace two strings iteratively
def laceStrings(s1, s2):
    shorter, longer = sorted([s1, s2], key=len)
    output = []
    for i in range(len(shorter)):
        output.append(s1[i])
        output.append(s2[i])
    output += longer[len(shorter):]
    return "".join(output)

# 5. Interlace two strings recursively
def laceStringsRecur(s1, s2):
    def helpLaceStrings(s1, s2, out):
        if s1 == '':
            return out + s2
        if s2 == '':
            return out + s1
        else:
            return helpLaceStrings(s1[1:], s2[1:], out + s1[0] + s2[0])
    return helpLaceStrings(s1, s2, '')

# 7. McNuggets
def McNuggets(n):
    if n < 0:
        return False
    elif n == 0:
        return True
    else:
        return any(McNuggets(n - x) for x in [20, 9, 6])