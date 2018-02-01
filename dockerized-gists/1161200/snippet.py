# *.* coding: utf-8 *.*

def letras(numero):
	if numero <= 9:
		return str(numero)
	elif numero == 10:
		return "A"
	elif numero == 11:
		return "B"
	elif numero == 12:
		return "C"
	elif numero == 13:
		return "D"
	elif numero == 14:
		return "E"
	else:
		return "F"

def reversa(texto):
	resultado = ""
	for c in texto:
		resultado = c + resultado
	return resultado

# El segundo parametro se usa para especificar la base del sistema numerico, por
# ejemplo, para el binario es el 2 y el Hexadecimal el 16.
def decAtodo(numero, base):
	if base < 2:
		return "Error"

	resultado = ""
	auxiliar, residuo = 0, 0

	while True:
		auxiliar = numero
		numero /= base
		residuo = auxiliar % base

		resultado += letras(residuo)
		if numero <= 1:
			if numero == 1 and base != 2:
				resultado += letras(numero)
			elif numero <= 1 and base == 2:
				resultado += letras(numero)
			break;

	return reversa(resultado)