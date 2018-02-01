import sys

def func(a, sign, b):
	if a == '1':
		return (b, sign)
	if b == '1':
		return (a, sign)
	if a == 'i' and b == 'j':
		return ('k', sign)
	if a == 'j' and b == 'i':
		return ('k', -1 * sign)
	if a == 'k' and b == 'i':
		return ('j', sign)
	if a == 'i' and b == 'k':
		return ('j', -1 * sign)
	if a == 'j' and b =='k':
		return ('i', sign)
	if a == 'k' and b =='j':
		return ('i', -1 * sign)
	if a == 'i' and b == 'i':
		return ('1', -1 * sign)
	if a =='j' and b =='j':
		return ('1', -1 * sign)
	if a == 'k' and b =='k':
		return ('1', -1 * sign)

cases = int(raw_input())
for c in xrange(cases):
    # read in misc problem constants
    x, y = map(int, raw_input().split())
    z = map(str, raw_input())

    res = '1'
    sign = 1

    period = y

    aa = False
    bb = False
    cc = False

    for i in xrange(y):
    	for j in z:
            res, sign = func(res, sign,  j)

        if res == '1' and sign == 1:
            period = i + 1
            break;

    l = y % period

    # two periods
    mm = '1'
    nn = 1
    for i in xrange(2 * period):
        for j in z:
            mm, nn = func(mm, nn, j)
            if mm == 'i' and nn == 1:
                aa = True
            if (aa == True and mm == 'k' and nn == 1):
                bb = True


    # print l

    if (l > 0):
        res = '1'
        sign = 1
        for i in xrange(l):
            for j in z:
                res, sign = func(res, sign,  j)

    # print y, period, c+1, aa, bb, res, sign

    if aa == True and bb== True and res == '1' and sign == -1:
        print "Case #%d: YES" % (c+1)
    else:
        print "Case #%d: NO" % (c+1)