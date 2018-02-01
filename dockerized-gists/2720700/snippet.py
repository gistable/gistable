def merge(left, right):
	if not len(left) or not len(right):
		return left or right

	result = []
	i, j = 0, 0
	while (len(result) < len(left) + len(right)):
		if left[i] < right[j]:
			result.append(left[i])
			i+= 1
		else:
			result.append(right[j])
			j+= 1
		if i == len(left) or j == len(right):
			result.extend(left[i:] or right[j:])
			break 

	return result

def mergesort(list):
	if len(list) < 2:
		return list

	middle = len(list)/2
	left = mergesort(list[:middle])
	right = mergesort(list[middle:])

	return merge(left, right)

if __name__ == "__main__":
	print mergesort([3,4,5,1,2,8,3,7,6])