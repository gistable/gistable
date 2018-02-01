def disjoint(A,B):
	i,j= 0,0
	while i < len(A) and j < len(B):
		if A[i] == B[j]:
			return False
		if A[i] > B[j]:
			j += 1
		else:
			i += 1
	return True