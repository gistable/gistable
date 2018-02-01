# Function Practice Send and Return Values w/Booleans
# Please create and call various functions as explained below.
import os
os.system("clear")

# 1
# Write a function that prints Doh! on the screen.  
# Call the function print_doh
print("1\n")
def print_doh():
	pass

print_doh()

# 2
# Write a function that will print "You are tall." if a person is tall
# If the person is not tall, print "You are not tall."
# You must ask the user his or her height OUTSIDE of the function.
# Call the function print_height_result
print("\n2\n")
def print_height_result(height):
	pass

height = int(input("How tall are you in cm.? > "))
print_height_result(height)

# 3
# Write a function that will determine the winner of a Janken round
# For example, if the user chooses R and the computer chooses S
# Print "The user wins!"
# If it is a tie, print "Tie!"
# Call the function print_winner
print("\n3\n")
def print_winner(user_choice, computer_choice):
	pass
	
print_winner("R", "R") #Tie
print_winner("R", "P") #Computer wins
print_winner("R", "S") #User wins
print_winner("P", "R") #User wins
print_winner("P", "P") #Tie
print_winner("P", "S") #Computer wins
print_winner("S", "R") #Computer wins
print_winner("S", "P") #User wins
print_winner("S", "S") #Tie

# 4
# Write a function that checks if a string is all UPPERCASE
# If so, return True
# If not, return False
# Call the function is_upper
print("\n4\n")
def is_upper(string):
	pass
	
if is_upper("SYMBAS"):
	print("SYMBAS is uppercase.")
else:
	print("SYMBAS is not uppercase.")
	
if is_upper("Symbas"):
	print("Symbas is uppercase.")
else:
	print("Symbas is not uppercase.")

# Bonus
# Write a function that checks if a string is a palindrome
# A palindrome is a word that is the same backwards and forwards
# If so, return True
# If not, return False
print("\nBonus\n")
def is_palindrome(string):
	pass
	
if is_palindrome("sassafrass"):
	print("sassafrass is a palindrome.")
else:
	print("sassafrass is not a palindrome.")
	
if is_palindrome("racecar"):
	print("racecar is a palindrome.")
else:
	print("racecar is not a palindrome.")
	
print("\n\n\n\n")
