#Usage: paren(0,4,'')
def paren(sum,remaining,str):
   	if sum < 0:
	    return
	if remaining == 0:
	    print str+')'*sum
	    return
	paren(sum+1,remaining-1,str+'(')
	paren(sum-1,remaining,str+')')