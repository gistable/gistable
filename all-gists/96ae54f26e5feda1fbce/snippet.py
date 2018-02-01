for test in range(input()):
    N = input()
    A = map(int, raw_input().split())
    ans = 0
    for i in range(N):
        l = 0
        r = 0
        for j in range(N):
            if A[j]>A[i]:
                if j<i:
                    l += 1
                else:
                    r += 1
        ans += min(l, r)
    print "Case #%s: %s" % (test+1, ans)
