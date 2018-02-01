def merge_sort(aList):

	if len(aList) < 2:
		return aList
	else:
		middle = len(aList)/2
		left = aList[:middle]
		right = aList[middle:]

		left = merge_sort(left)
		right = merge_sort(right)
		return list(merge(left, right))
		

def merge(left, right):
	result = []
	left_index = 0
	right_index = 0

	while left_index < len(left) and right_index < len(right):
		
		if left[left_index] <= right[right_index]:
			result.append(left[left_index])
			left_index+=1
		else:
			result.append(right[right_index])
			right_index+=1

	if left:
		result.extend(left[left_index:])
	if right:
		result.extend(right[right_index:])

	return result

def main():
	myL = [45,1,43,89,2,43,13]
	print merge_sort(myL)

if __name__ == '__main__':
	main()