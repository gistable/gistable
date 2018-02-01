def partition(a, p, q):
	pivot = a[q-1]
	i = p-1

	for j in range(p, q-1):
		if a[j] < pivot:
			i += 1
			t = a[j]
			a[j] = a[i]
			a[i] = t

	t = a[q-1]
	a[q-1] = a[i+1]
	a[i+1] = t
	return i+1


def qsort(a, p, q):
	if p >= q:
		return

	r = partition(a, p, q)
	qsort(a, p, r-1)
	qsort(a, r+1, q)


a = [2, 8, 14, 5, 9, 6, 15, 7, 7, 7, 123, 12, 4]

print a
qsort(a, 1, len(a))
print a