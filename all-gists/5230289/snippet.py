n = int(raw_input())
N = map(int, raw_input().split())
m = int(raw_input())
M = map(int, raw_input().split())

# t[r][c] stores the LCIS that *** ends with M[r] *** between N[0..c} and M[0..r]
t = [[0 for i in xrange(n)] for j in xrange(m)]
pre = [-1 for i in xrange(m)]
for r in xrange(m):
    # p is the len of LCIS that ends with M[r] seen so far
    p = 0
    for c in xrange(n):
        if M[r] == N[c]:
            if r == 0 or c == 0:
                p = 1
            else:
                # p2 stores the max len of LCIS that appears before r and ends with a value < M[r]
                p2 = 0
                for i in xrange(r):
                    if M[i] < M[r]:
                        if p2 < t[i][c - 1]:
                            p2 = t[i][c - 1]
                            pre[r] = i
                # update p with p2
                p = max(p, p2 + 1)
        t[r][c] = p

maxL = 0
maxIndex = -1
for r in xrange(m):
    if maxL < t[r][n - 1]:
        maxL = t[r][n - 1]
        maxIndex = r
print maxL
indices = list()
while maxIndex != -1:
    indices.append(maxIndex)
    maxIndex = pre[maxIndex]
for i in reversed(indices):
    print M[i],