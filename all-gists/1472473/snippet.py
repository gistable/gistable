class Node:
      def __init__(self, info, left=None,right=None):
          self.info = info
          self.left = left
          self.right = right

      def __call__(self, left=None, right=None):
          self.left = left
          self.right = right  
          return self.info
out = []

def _inorder(node):
    if node:
       _inorder(node.left)
       out.append(node.info) 
       _inorder(node.right)

def _preorder(node):
    if node:
        out.append(node.info) 
        _preorder(node.left)
        _preorder(node.right)

def _postorder(node):
    if node:
        _postorder(node.left)
        _postorder(node.right)
        out.append(node.info) 

'''
                      F
                 B       G
              A    D        I
                 C   E     H 
'''
 
_ = None
A = Node('A')
B = Node('B')
C = Node('C')
D = Node('D')
E = Node('E')
F = Node('F')
G = Node('G')
H = Node('H')
I = Node('I')

F(B,G)
B(A,D)
D(C,E)
G(_,I)
I(H,_)

print 'Inorder:'
_inorder(F)
print out
out = []
print 'Preorder:'
_preorder(F)
print out
out = []
print 'Postorder:'
_postorder(F)
print out