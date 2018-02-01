from math import sqrt

def is_prime(digit):

	if digit == 1:
		return False
	loop_limit = int(sqrt(int(digit)))

	for x in range(2, loop_limit + 1):
		if digit % x == 0:
			return False
	return True



def pandigital_prime():

	list_of_lists = []

	for x in range(1, 10):

		temp_list = []
		temp_list.extend(range(1, 10)[:x])
		list_of_lists.append(temp_list)

	for x in range(7654321, 1, -2):
		sorted_list = sorted([int(y) for y in list(str(x))])
		if sorted_list in list_of_lists:
			if is_prime(x):
				return x


print pandigital_prime()