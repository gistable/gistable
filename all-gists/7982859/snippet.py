def print_permutations(str):
	if(len(str) == 1): return [str]
	perms = print_permutations(str[1:])
	return [x[0:i]+str[0]+x[i:] for x in perms for i in range(len(x)+1)]

print print_permutations("abc")	