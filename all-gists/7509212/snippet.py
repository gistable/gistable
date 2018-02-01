def next_greater(arr):
	while(not is_rev_sorted(arr)):
		for i in reversed(range(len(arr) - 1)):
			if arr[i] < arr[i+1]: break
		for j in reversed(range(len(arr))):
			if arr[i] < arr[j]: break
		swap(arr, i, j)
		yield reverse(arr, i+1)

def swap(arr, i, j): arr[i], arr[j] = arr[j], arr[i]

def reverse(arr, i):
	j = len(arr) - 1
	while( i < j):
		swap(arr, i, j)
		i+=1; j-=1
	return arr

def is_rev_sorted(arr):
	rev=True
	for i in range(len(arr) - 1):
		if arr[i] < arr[i+1]:
			rev=False
			break
	return rev

a = [1,2,3,4]
for i in next_greater(a):
	print i
