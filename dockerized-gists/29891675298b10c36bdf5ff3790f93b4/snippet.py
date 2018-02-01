
class A(object):
     k = None
     def __init__(self,k):
         self.k = k
     def __eq__(self, other):
         return self.k == other.k

      
source_items = [A(i) for i in [1,2,3,4,3,2,3,6]]
unduplicate_items = [elem for ind,elem in enumerate(source_items) if ind == source_items.index(elem)]

for i in unduplicate_items:
     print(i.k)
# Out: [1,2,3,4,6]