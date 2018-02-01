import sys

# Facebook Hacker Cup Qualification Round - Studious Student
# http://www.facebook.com/hackercup/problems.php?round=4

def lex_compare(x, y):
    if x.startswith(y) and x != y:
        return lex_compare(x[len(y):], y)

    if y.startswith(x) and y != x:
        return lex_compare(x, y[len(x):])

    if x < y:
        return -1

    if x > y:
        return 1

    return 0

def main():
    with open(sys.argv[1]) as fp:
        lines = fp.readlines()

        n = lines[0]

        for x in range(1,int(n)+1):
            words = lines[x].split()
            m = words[0]
            words = words[1:int(m)+1]
            lex = "".join(sorted(words,cmp=lex_compare))
            print lex

if __name__ == '__main__':
    main()