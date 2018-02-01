# Python Noob Generator by rubenwardy
# License: WTFPL
# See IRC bot using this: https://gist.github.com/rubenwardy/8863c20a75e4faad3562

# Example:
### a random team mate shot your mum also dat enemy scouted a
### random gun and a random gun covered a random gun but also your
### mum nuked dat arsehole also a random thingy ran it like a arsehole blew up a kid


# Todo:
#  * Adjectives - crappy, fishy, rubbish, stupid
#  * a/an


cons = [
	"oh yeah",
	"and",
	"also",
	"i don't know but",
	"but also",
	"and then",
	"but then",
	"but maybe",
	"also that",
	"but uh",
	"probs",
	"yeah like",
	"like",
	"but you dont understand it was like",
	""
]

nouns = [
	"guy",
	"gun",
	"assassin",
	"enemy",
	"soldier",
	"dragon",
	"ninja",
	"team mate",
	"xbox",
	"it",
	"playstation",
	"thingy",
	"hacker",
	"griefer",
	"noob",
	"mum",
	"arsehole",
	"butt",
	"kid"
]

verbs = [
	"ran",
	"shot",
	"blew up",
	"killed",
	"scouted",
	"covered",
	"nuked",
	"destroyed"
]

prefixes = [
	"the",
	"this",
	"a",
	"a random",
	"dat"
]

result = ""

import random

def getrand(array):
	return array[ round( random.random() * len(array) - 0.5 ) ]
	
def getnoun():
	noun = getrand(nouns)
	if (noun == "it"):
		pass
	elif (noun == "mum"):
		noun = "your mum"
	else:
		noun = getrand(prefixes) + " " + noun
	return noun
	
def gensentence():	
	noun1 = getnoun()
	noun2 = getnoun()
	verb = getrand(verbs)
	return noun1 + " " + verb + " " + noun2
	
def dooptions():
	global result
	print("\n")
	print("'exit' - exit program")
	print("'save' - save to text file")
	print("blank - new section")
	res = input("> ")
	if res == "exit":
		return False
	elif res == "save":
		file = input("File name (remember .txt on the end): ")
		f = open(file,"w")
		f.write(result)
		f.write("\n") # linux file endings
		f.close() 
	else:
		con = getrand(cons)
		if con != "":
			con = " " + con
		result += con
		result += " " + gensentence()
		
	return True

################
# MAIN PROGRAM #
################
if __name__ == "__main__":
	result = gensentence()
	print("Enter the number of sentences you want to create initially.")
	print("You can still add sentences after this.\n")
	doamount = int(input("> "))

	for x in range(doamount):
		result += " " + getrand(cons)
		result += " " + gensentence()
		
	print("\n" + result)

	while (dooptions()):
		print("\n")	
		print(result)
