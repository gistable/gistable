#Kata with Up1 - Agile Thailand 2014 @ Eng CU
#Sat 7 June 2014

class FizzBuzzFactory():
	def create(self):
		rules = [FizzBuzzBangRule(), BuzzBangRule(), FizzBangRule(), FizzBuzzRule(),
			 BangRule, BuzzRule(),FizzRule(),NormalRule()]
		return FizzBuzz(rules)

class FizzBuzz():
	def __init__(cls,rules):
		cls.rules = rules

	def say(self,x):
		for rule in self.rules:
			if rule.is_handle(x):
				return rule.say(x)

class Rule():
	def is_handle(self,x):
		pass

	def say(self,x):
		pass

class NormalRule(Rule):
	def is_handle(self,x):
		return True

	def say(self,x):
		return x

class FizzRule(Rule):
	def is_handle(self,x):
		return x % 3 == 0

	def say(self,x):
		return "Fizz"

class BuzzRule(Rule):
	def is_handle(self,x):
		return x % 5 == 0

	def say(self,x):
		return "Buzz"
		
class BangRule(Rule):
	def is_handle(self,x):
		return x % 7 == 0

	def say(self,x):
		return "Bang"

class FizzBuzzRule(Rule):
	def is_handle(self,x):
		return x % 5 == 0 and x % 3 == 0

	def say(self,x):
		return "FizzBuzz"
		
class FizzBangRule(Rule):
	def is_handle(self,x):
		return x % 7 == 0 and x % 3 == 0
	def say(self,x):
		return "FizzBang"
		
class BuzzBangRule(Rule):
	def is_handle(self,x):
		return x % 7 == 0 and x % 5 == 0
	def say(self,x):
		return "BuzzBang"
		
class FizzBuzzBangRule(Rule):
	def is_handle(self,x):
		return x % 7 ==0 and x % 5 == 0 and x % 3 == 0
 
	def say(self,x):
		return "FizzBuzzBang"


if __name__ == '__main__':
	l = [1,2,3,6,5,15,20]
	fizz_buzz = FizzBuzzFactory().create()
	for x in l:
		print(fizz_buzz.say(x))
