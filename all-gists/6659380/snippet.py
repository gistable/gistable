class Node():

	def __init__(self,key):
		self.key = key
		self.left = None
		self.right = None
		self.parent = None
		

class Tree():

	def __init__(self):
		self.root = None		

	def add_node(self,key,node=None):

		if node is None:
			node = self.root
		
		if self.root is None:
			self.root = Node(key)

		else:
		
			if key <= node.key :
				if node.left is None:
					node.left = Node(key)
					node.left.parent = node
					print "left"
					return 
				else:
					# return self.add_node(key,node = self.root.left)
					return self.add_node(key,node = node.left)
			else:
				if node.right is None:
					node.right = Node(key)
					node.right.parent = node
					print "right"
					return 
				else:
					# return self.add_node(key,node = self.root.right)
					return self.add_node(key,node = node.right)

	
	def search(self,key,node = None):

		if node is None:
			node = self.root

		if self.root.key == key:
			print "key is at the root"
			return self.root
		
		else:
			if node.key == key :
				print "key exists"
				return node

			elif key < node.key and node.left is not None:
				print "left"
				return self.search(key,node = node.left)
			
			elif key > node.key and node.right is not None:
				print "right"
				return self.search(key,node = node.right)
			
			else:
				print "key does not exist"
				return None

	def delete_node(self,key,node=None):
		#search for the node to be deleted in tree
		if node is None:
			node = self.search(key)#return the node to be deleted

		#root has no parent node	
		if self.root.key == node.key: #if it is root
			parent_node = self.root
		else:
			parent_node = node.parent
			

		'''case 1: The node has no chidren'''
		if node.left is None and node.right is None:
			if key <= parent_node.key:
				parent_node.left = None
			else:
				parent_node.right = None
			return

		'''case 2: The node has children'''
		''' if it has a single left node'''
		if node.left is not None and node.right is None :
			if node.left.key < parent_node.key : 
				parent_node.left = node.left
			else:
				parent_node.right = node.left

			return

		'''if it has a single right node'''
		if node.right is not None and node.left is None:
			if node.key <= parent_node.key:
				parent_node.left = node.right
			else:
				parent_node.right = node.right
			return

		'''if it has two children'''
		'''find the node with the minimum value from the right subtree.
		   copy its value to thhe node which needs to be removed.
		   right subtree now has a duplicate and so remove it.'''
		if node.left is not None and node.right is not None:
			min_value = self.find_minimum(node)
			node.key = min_value.key
			min_value.parent.left = None
			return


	def find_minimum(self,node = None):
		
		if node is None:
			node = self.root

		'''find mimimum value from the right subtree'''
		
		'''case when there is only a root node'''
		if node.right is not None:
			node = node.right
		else:
			return node

		if node.left is not None:
			return self.find_minimum(node = node.left)
		else:
			return node

	def tree_data(self,node=None):
		if node is None:
			node = self.root

		stack = []
		while stack or node:
			if node is not None:
				stack.append(node)
				node = node.left
			else:
				node = stack.pop()
				yield node.key
				node = node.right



		
			
t=Tree()
t.add_node(10)
t.add_node(13)
t.add_node(14)
t.add_node(8)
t.add_node(9)
t.add_node(7)
t.add_node(11)

'''
10---8---7
  |	 |
  |	 ---9
  ---13---11
  	   |
  	   ---14	
'''