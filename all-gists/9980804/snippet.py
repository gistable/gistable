
print "Hola"
estado= None
y= None

while 1:
	A= input ("Dame el valor de A")
	B= input ("Dame el valor de B")

	if A==1:
		estado= "entra"
		while B==0 and y!= "salir":
			print "ciclo 1"
			B=input("Dame el valor de B")
			if B==1:
				A=0
				while B==1:
					B=input("Dame el valor de B") 
					print "Ciclo 2"
				y= "salir"

	y=None
			
	if B==1:
			estado= "sale"
			while A==0 and y!= "salir":
				print "ciclo 1"
				A=input("Dame el valor de A")
				if A==1:
					B=0
					while A==1:
						A=input("Dame el valor de A")
						print "Ciclo 2"
					y= "salir"


	print estado
	estado= None




