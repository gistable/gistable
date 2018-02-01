class Node:
  def __init__(self, key):
      self.key = key
      self.parent = None
      self.left = None
      self.right = None


def insert(root, t):
  new = Node(t)
  if root == None:
      root = new
  else:
      node = root
      while True:
        if t < node.key:
        # go left
          if node.left == None:
            node.left = new
            node.parent = node
            break
          node = node.left
        else:
        # go right
          if node.right is None:
            node.right = new
            node.parent = node
            break
          node = node.right
  return new

def find(root, t):
  node = root
  if t == node.key:
    return node
  while node is not None:
    if t == node.key
      return node
    elif t < node.key:
      node = node.left
    else:
      node = node.right
  return node


def get_height(root):
  if root == None:
    return 0
  return max(get_height(root.left), get_height(root.right)) + 1

def is_balanced(root):
  if root == None:
    return True
  height_diff = get_height(root.left) - get_height(root.right)
  
  if abs(height_diff) > 1:
    return False
  else:
    return is_balanced(root.left) and is_balanced(root.right)

 self.root = root
