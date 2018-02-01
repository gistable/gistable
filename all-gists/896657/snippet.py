# The following will have an average running time of T(n) = O(n^log(6,0.83)) = O(n^9.8)
def gravitysort(l, i=0, j=0):
	if not j: j = len(l)-1
	if l[j] < l[i]: swap(l, i, j)
	if j-i > 1:
		t = (j-i+1)/6
		gravitysort(l, i, j-t)
		gravitysort(l, i+t, j)
		gravitysort(l, i, j-t)
		gravitysort(l, i+t, j)
		gravitysort(l, i, j-t)
		gravitysort(l, i+t, j)
	return l

#Amortization using 2 passes and insertion sort on the nearly sorted
# T(n) = 2*T(5n/6) + O(n^2) -- assuming worst/avg case scenario for insertion sort, in which case we use Theta(n^2) =^= n^2
# f(n) = O(5n/6 + n^2) = O(n^3.8) -> T(n) = O(n^3.8)

#Quicksort is a special variation of this in which
# T(n) = 2*T(n/2) + O(n) -> T(n) = theta(n * logn)