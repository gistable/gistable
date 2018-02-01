# Factorial de 'n'
def factorial(n):
	if n == 0:
		return 1
	return factorial(n - 1) * n

# Para cada número a revisar
for i in range(1, 2500000 + 1):

	# Calculamos según la definición
	j = sum([factorial(ord(j) - 48) for j in "%i" % i])

	# Y si coincide
	if i == j:

		# ¡Es un factorión!
		print(i)
