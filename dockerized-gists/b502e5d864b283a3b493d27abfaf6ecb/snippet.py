# Definition for a binary tree node.
# class TreeNode(object):
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution(object):
        
    def mergeTrees(self, t1, t2):
        """
        :type t1: TreeNode
        :type t2: TreeNode
        :rtype: TreeNode
        """
        if not t1 and not t2: return None
        t = TreeNode((t1.val if t1 else 0) + (t2.val if t2 else 0)) 
        t.left = self.mergeTrees(t1.left if t1 else None, t2.left if t2 else None)
        t.right = self.mergeTrees(t1.right if t1 else None, t2.right if t2 else None)
        return t