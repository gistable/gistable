#using list functions
def sort(a):

	i = 1
	while(i < len(a)):
		if i < 1: i = i + 1

		else:
			p = i - 1
			if a[i] < a[p]:
				e = a.pop(p)
				a.append(e)
				i = i - 1
			else:
				i = i + 1
	
	return a

a = [7,1,3,5,2,8]
print(sort(a))

#without using list functions:
def sort(a):

	i = 1
	while(i < len(a)):
		if i < 1: i = i + 1

		else:
			p = i - 1
			if a[i] < a[p]:
				c = a[i] 
				l = a[p]
				a[p] = c
				a[i] = l
				i = i - 1
			else:
				i = i + 1
	
	return a

a = [7,1,3,5,8,2]
print(sort(a))