class Node:
  def __init__(self, data):
    self.data = data
    self.left = None
    self.right = None
    

def insert(root, data):
  node = Node(data)
  
  if root is None:
    root = node
  if root.data > data:
    if root.left is None:
      root.left = node
    else:
      insert(root.left, data)
  else:
    if root.right is None:
      root.right = node
    else:
      insert(root.right, data)

def search(root, data):
  if root is None:
    return None
  if root.data < data:  return search(root.right, data)
  elif root.data > data:  return search(root.left, data)
  else: return root.data

def inOrderPrint(root):
  if not root:
    return
  inOrderPrint(root.left)
  print(root.data)
  inOrderPrint(root.right)
  
def preOrderPrint(root):
  if root is None:
    return
  print(root.data)
  preOrderPrint(root.left)
  preOrderPrint(root.right)

def postOrderPrint(root):
  if root is None:
    return
  postOrderPrint(root.left)
  postOrderPrint(root.right)
  print(root.data)
  
  
r = Node(3)
insert(r, 7)
insert(r, 1)
insert(r, 5)

print("inOrderPrint")
inOrderPrint(r)
print("preOrderPrint")
preOrderPrint(r)
print("postOrderPrint")
postOrderPrint(r)
print('Search 9:')
print(search(r, 9))
