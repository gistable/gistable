# This is a meal planner to help me decide what to eat for dinner.  I don't like to 
# waste a lot of time thinking about what to cook, so this would ideally help me create a 
# varied menu without too much deliberation.

import datetime
import random

class Food:
	def __init__(self,name,group = None,health = None, price = None, preptime = None):
		# name of food
		self.name = str(name)
		
		# group = protein, vegetable, or carbohydrate
		self.group = group
		
		# health is a rating on a scale of 1 (unhealthiest) to 10 (healthiest)
		self.health = health
		
		# price is in dollars
		self.price = price
		
		# preptime in minutes
		self.preptime = preptime
		
		
# a meal contains several foods & will generally have a protein, a vegetable, and a carbohydrate
class Meal:
	def __init__(self,foods = [], date = None):
		self.foods = foods
		self.date = date
		self.get_health()
		self.get_price()
		self.get_preptime()
	
	def add_date(self, date):
		self.date = date
		
	def get_health(self):
		self.health = sum([i.health for i in self.foods if i])
		
	def get_price(self):
		self.price = sum([i.price for i in self.foods if i])
		
	def get_preptime(self):
		if len(self.foods) != 0:
			self.preptime = max([i.preptime for i in self.foods if i])
		
	def add_food(self, food):
		self.foods.append(food)
		self.get_health()
		self.get_price()
		self.get_preptime()
	
		
	def print_meal(self):
		print 'Foods: %s, %s, and %s.' % (self.foods[0].name, self.foods[1].name, self.foods[2].name) 
		print 'This meal scores a %i out of 30 for health, and costs $%d.' % (self.health, self.price ) 
		print 'This meal takes %i minutes to prepare.' % (self.preptime )
		
 
# stores current collection of food and also provides access to this collection through get_meal and get_food
class Pantry:
	def __init__(self, foods=[]):
		self.contents = [i for i in foods]
		self.price = sum([i.price for i in foods if i])
		self.get_health()
		self.meals = []

	def get_health(self):
		groups = [f.group for f in self.contents]
		self.versatility = len(set(groups))

	def __call__(self,*newfoods):
		self.contents += newfoods
		self.price += sum([i.price for i in newfoods])
		self.get_health()
		
	def get_meal(self):
		protein = self.get_food('protein')
		vegetable = self.get_food('vegetable')
		carbohydrate = self.get_food('carbohydrate')
		meal = Meal([protein, vegetable, carbohydrate])
		return meal
		
	# random choice of food from collection in pantry, specified by group	
	def get_food(self, group):
		food = self.contents[random.randint(0, len(self.contents) - 1)]
		if food.group == group:
			return food
		else:
			return self.get_food(group)
			
# interacts with the user through propose_meal and keeps history of meals eaten on specific dates	
class FoodPlanner:
	def __init__(self, history=[], pantry=None, user = None, currentmeal = None):
		self.history = history
		self.pantry = pantry
		self.user = user
		self.currentmeal = currentmeal
	
	def add_pantry(self, pantry):
		self.pantry = pantry
		
	def add_user(self, user):
		self.user = user
	
	def add_meal_to_history(self, meal):
		self.history.append(meal)
	
	# user interaction facilitates meal rejection & acceptance
	def propose_meal(self):
		meal = self.pantry.get_meal()
		meal.print_meal()
		print 'Do you want this meal tonight, %s? Say Yes or No' % self.user
		answer = raw_input('>')
		if answer.lower() == 'yes':
			print 'I have added this meal to your food history.  Enjoy!'
			meal.add_date(datetime.date.today())
			self.add_meal_to_history(meal)
		if answer.lower() == 'no':
				print 'OK! Picking a new meal for you now.'
				self.propose_meal()
				
	def view_history(self):
		for i in self.history:
			print 'On %s, you ate:' % (str(i.date))
			i.print_meal()
			
			
			
#testing	
myFoodPlanner = FoodPlanner()
testFoods = [Food('chicken', 'protein', 8, 5.00, 15), Food('kale', 'vegetable', 10, 5.00, 3),
			Food('rice', 'carbohydrate', 5, 3.00, 20), Food('salmon', 'protein', 9, 7.00, 25),
			Food('spinach', 'vegetable', 10, 4.00, 10), Food('pasta', 'carbohydrate', 3, 2.00, 15),
			Food('steak', 'protein', 5, 8.00, 25), Food('carrots', 'vegetable', 9, 4.00, 2),
			Food('potatoes', 'carbohydrate', 4, 3.00, 15), Food('pork', 'protein', 6, 6.00, 20),
			Food('peppers', 'vegetable', 8, 2.00, 10)]
myPantry = Pantry(testFoods)
myFoodPlanner.add_pantry(myPantry)
myFoodPlanner.add_user('Samantha')
for i in xrange(2):
	myFoodPlanner.propose_meal()

myFoodPlanner.view_history()

