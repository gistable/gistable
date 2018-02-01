def quicksel(l,k):
    if len(l) <k:
		raise ValueError
    else:
		pivot=l.pop()         
		lg=filter(lambda x:x>pivot,l)         
		ll=filter(lambda x:x<=pivot,l)         
		if len(lg)>=k:
			return quicksel(lg,k)
		elif len(lg)+1==k:
			return pivot         
		else:             
			return quicksel(ll, k-len(lg)-1)
        
	

print quicksel([5,3,2,1,4,6,2,7,9,2,11],2) 