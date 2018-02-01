def subseq_cres_long(seq, k):
 	contador = 0
 	for i in range(1, len(seq)):
 		if(seq[i -1] < seq[i]):
 			contador += 1
 			if(contador == k):
 				return True
 	return False