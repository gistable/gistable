str_numbers = raw_input("ingrese una secuencia de numeros separados por espacios:")
numbers = []
for sn in str_numbers.split():
	try:
		n = int(sn)
	except:
		n = 0
	numbers.append(n)

def pares(numbers,i = 0):
	if len(numbers)-1 >= i:
		if numbers[i] % 2 == 0:
			print numbers[i]
		pares(numbers,i+1)

pares(numbers)