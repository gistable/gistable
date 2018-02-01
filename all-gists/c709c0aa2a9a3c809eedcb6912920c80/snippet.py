'''
Interview hack: Memorize preorder/inorder/postorder tree ITERATORS (no recursion) and their reverses.
It simplifies a disproportionate number of questions to simple for loops (see below).

I consider the implementations below the simplest way to memorize the iterative tree traversal algorithms,
because they are so similar to each other, and to their respective recursive versions.

Notes:
- We only visit a node after we have expanded its children (i.e. added them to the stack) in the desired order.
- `x is curr` does the expanded flagging for us, because we always expand the current node.
- It's possible to do this without this `expanded` bool, but I think this is the simplest by far (especially for postorder).
- The bool is basically the same as the return address in the recursive solution - not overhead worth worrying about.
- We add nodes to stack in reverse order because we will pop them in the reverse of the order added.
- My definition of reverse_preorder yields the parent first still (then right, left) as it makes more sense for structural comparison.
- A true reverse order iterator is better than simply reversing the collected values of the normal iterator for memory reasons.
- These traversals are basically DFS implementations, but we don't need a "visited" set thanks to trees being acyclic.

Related Questions:
- Write a non-recursive preorder/inorder/postorder binary tree traversal.
- Verify preorder/inorder/postorder sequence (given as array) in BST.
- Verify that a binary tree is a BST (x_(i-1) < x_i for x_i in inorder(t)).
- Find the kth smallest element of BST (counter and inorder(t)).
- Find the kth largest element of BST (counter and reverse_inorder(t)).
- Count the number of nodes (or full/leaf only).
- Check two trees are equivalent (inorder(a) == inorder(b) and pre/postorder(a) == pre/postorder(b)).
- Check if tree is symmetric (as above, but compare root.left with reverse iterators of root.right)
- Flatten Binary Tree to Linked List (in place - inorder, update pointers to point to next element).
- Find if there is a cycle in what would otherwise be a binary tree (slow + fast traversal over tee'd iterator).
- Find the preorder/inorder/postorder successor of a node (can be done faster than O(N) in a BST if we search first).
- https://leetcode.com/problems/binary-tree-vertical-order-traversal/

Extra Credit:
- Recursion can be elegant, but iterators are reusable, and won't exhaust the (limited) stack space.
- Your interviewer may ask you to implement recursive versions anyway - hacks are no substitute for actual practice!
- Ask if parent pointers are provided (as we can eliminate the stack that way). Usually this is a "no".
- You might want to mention "Morris inorder traversal" as an alternative inorder that uses O(1) space (no stack, but destroys tree).
- I doubt you would need to implement Morris inorder traversal, but here is a good guide: https://www.youtube.com/watch?v=wGXB9OWhPTg
'''

def tree_iterator(root, expand):
  stack = [(False, root)]
  while stack:
    expanded, curr = stack.pop()
    if not curr: continue
    if expanded: yield curr
    else: stack.extend([(x is curr, x) for x in reversed(expand(curr))])

preorder  = lambda root: tree_iterator(root, lambda node: (node,      node.left,  node.right))
inorder   = lambda root: tree_iterator(root, lambda node: (node.left, node,       node.right))
postorder = lambda root: tree_iterator(root, lambda node: (node.left, node.right, node))

reverse_preorder  = lambda root: tree_iterator(root, lambda node: (node,       node.right, node.left))
reverse_inorder   = lambda root: tree_iterator(root, lambda node: (node.right, node,       node.left))
reverse_postorder = lambda root: tree_iterator(root, lambda node: (node.right, node.left,  node))



'''
Incomplete stuff follows...

Todo:
- Add concrete solutions to above questions (to show just how much easier things are).
- Show version which lets you search for a key first and then continue traversal from that (while still visiting parents)
- Add predicate parameter to yield if node is a leaf, isnt a leaf, etc, and questions that are solvable with that.
- Add simple implementations of other commonly useful things (Lowest Common Ancestor, Breadth First iterator - a.k.a. level order).
- A single level order traversal will verify equal BSTs (not basic binary trees though).

Extension to generalise for BFS/level order and predicates:
Actually, it's easier to write predicates at the bottom level (e.g. map is_leaf to yielded nodes).
prune(x) function might help though? - can expand more than just two children -> DFS, sudoku (prune is if it is invalid board)
Mention that above are just DFS with visited information with node (avoids needing hashable node type)
'''

def tree_iterator(root, expand, fifo=False, predicate=lambda x:True):
  stack = [(False, root)]
  while stack:
    expanded, curr = stack.pop(0 if fifo else -1)
    if not curr: continue
    if expanded: not predicate(curr) or (yield curr)
    else: stack.extend([(x is curr, x) for x in [reversed,lambda x:x][fifo](expand(curr))])

level_order = lambda root: tree_iterator(root, lambda x: (x, x.left, x.right), True)

# But pretty easy to write directly:
# might be useful to signal end of a level somehow too (for linking level question)
def level_order(root):
  q = [root]
  f = lambda x: [q.extend([x.left, x.right]),x][1]
  return (f(x) for x in q if x) # and not prune(x)

is_leaf = lambda x:not x.left and not x.right
count_leaves = lambda root: sum(1 for _ in tree_iterator(root, lambda x: (x.left, x, x.right), predicate=is_leaf))