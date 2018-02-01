class Inventory:
	def __init__(self, items):
		self.items = items
		
	def show(self):
		print self.items
		
	'''
	Adds an item to the inventory if it is not full.
	'''
	def add_item(self, new_item):
		if len(self.items) < 12:
			self.items.append(new_item)
		else:
			print "Your inventroy is full."

	'''
	Removes an item from the inventory.
	'''
	def remove_item(self, del_item):
		for slot, item in enumerate(self.items):
			if item == del_item:
				self.items.pop(slot)
				break

	'''
	'Combines' items by removing two and adding another.
	'''
	def combine_item(self, component1, component2):
		mixed_item = ""
		for slot, item in enumerate(self.items):
			if item == component1:
				self.items.pop(slot)
				mixed_item += component1
				break
		for slot, item in enumerate(self.items):
			if item == component2:
				self.items.pop(slot)
				mixed_item += component2
				break
		if mixed_item == component1+component2:
			self.items.append(mixed_item)
		else:
			print "These items can't be combined"

'''
Interactive menu for UI.
'''
class Menu:
	exit_now = False
	items = ["Display Inventory", "Remove Item", "Combine Items", "Show Menu", "Exit Menu" ]
	
	
	def __init__(self, player):
		self.player = player
  
	def disp_inv(self):
		print self.inventory
    
	def item_combine(self):
		com_item1 = raw_input("Enter first component: ")
		com_item2 = raw_input("Enter second component: ")
		combine_item(self.inventory, com_item1, com_item2)

	def exit(self):
		self.exit_now = True

	def inventory_remove_item(self):
		item =  raw_input('Which item? ')
		self.player.inventory.remove_item(item)

	def select(self, item):
		menu = [self.player.inventory.show,
				self.inventory_remove_item,
				self.item_combine,
				self.show,
				self.exit,
			   ]
		menu[item - 1]()

	def show(self):
		for i, item in enumerate(self.items):
			print str(i+1)+".", item
		print

	
	menu = [disp_inv,
				inventory_remove_item,
				item_combine,
				show,
				exit,
			]


		
'''
Player data. Currently contains player inventory.
'''
class Player:
	def __init__(self, name, inventory):
		self.name = name
		self.inventory = inventory
	
player = Player('Bartleby The Silent',
				Inventory(["femur", "spidersilk", 
				"large arrowhead", "cookie"])
				)

menu = Menu(Player)

menu.show()
while not menu.exit_now: 
	choice = input("Enter your selection #: ")
	menu.select(choice)


	

	

