#Returns the sum of num1 + num2.
def add(num1, num2):
	return num1 + num2
	
#Returns the sum of num1 - num2.	
def min(num1, num2):
	return num1 - num2
	
#Returns the sum of num1 * num2.	
def mul(num1, num2):
	return num1 * num2
	
#Returns the sum of num1 / num2.	
def div(num1, num2):
	return num1 / num2
	
def goback():
	print ("Thank you for using this calculator")
	return main()


def main ():
	print ("What do you want to calculate? You can enter either +, -, *, /")
	operation = input()
	if (operation != '+' and operation != '-' and operation != '*' and operation != '/'):
		print ("You haven't entered a correct command" )
		return main()
		#Invalid operatin, and returns to main()
		
	else:
		num1 = int(input("Enter number one: "))
		num2 = int(input("Enter number two: "))		
		if(operation == '+'): #Select add as method
			print (add(num1, num2))
		elif(operation == '-'): #Select min as method
			print (min(num1, num2))
		elif(operation == '*'): #Select mul as method
			print (mul(num1, num2))
		else:
			print (div(num1, num2))


	
	

main() #starts the main menu

goback() #returns to main menu