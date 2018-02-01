from pwn import *
import re

class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

def buildtree(preorder):
	if len(preorder) == 0:
		return None
	if len(preorder) == 1:
		return TreeNode(preorder[0])
	root = TreeNode(preorder[0])
	preorder = preorder[1:]
	index = len(preorder)
	for i in xrange(len(preorder)):
		if (preorder[i] > root.val):
			index = i
			break
	root.left = buildtree(preorder[:index])
	root.right = buildtree(preorder[index:])
	return root

def traverse(node):
	if (node == None): return
	yield node.val
	for x in traverse(node.right):
		yield x
	for x in traverse(node.left):
		yield x

host = '188.166.133.53'
port = 11491

r = remote(host, port)
# banner
print r.recvline(timeout=2),
for i in xrange(50):
	s = r.recvline(timeout=2)
	print s,
	prob = re.findall(r'(\[[\d, ]+\])', s)[0]
	l = eval(prob)
	result = list(traverse(buildtree(l)))
	print str(result)
	r.sendline(str(result))
	print r.recvline(timeout=2),
print r.recvline(timeout=2),
