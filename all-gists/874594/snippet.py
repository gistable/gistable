
from collections import deque

try:
    set()
except:
    from sets import Set as set
    

        
def value_fn_from_array(data):
    """Returns a function that takes two parameters (y,x) and returns
        the value at that point"""
    return lambda y,x:data[y][x]

def find_regions_recur(value_fn, cols, rows):
    """Walks the data via the value_fn such that every point in 0 -> cols & 0-> rows
        is visited by calling value_fn(y,x). Returns a list of lists of turples (y,x)"""
    bags = []
    visited = set()
    
    def visit(bag,p):
        y,x = p
        
        if y < 0 or x < 0 or y >= len(data) or x >= len(data[y]):
            return
        
        if p in visited:
            return

        visited.add(p)
        
        if value_fn(y,x) > 0:
            bag.append(p)
            visit(bag,(y  ,x+1))
            visit(bag,(y+1,x+1))
            visit(bag,(y+1,x))
            visit(bag,(y+1,x-1))
            visit(bag,(y  ,x-1))
            visit(bag,(y-1,x-1))
            visit(bag,(y-1,x))
            visit(bag,(y-1,x+1))
      
    # processing loop starts here
    for y in range(0,rows):
        for x in range(0,cols):
            p = (y,x)
            if p not in visited:
                if value_fn(y,x) > 0:
                    bag = []
                    visit(bag,p)
                    bags.append(bag)
                else:
                    visited.add(p)
    return bags

def iter_regions(value_fn, cols, rows):
    """Walks the data via the value_fn such that every point in 0 -> cols & 0-> rows
        is visited by calling value_fn(y,x). yields list of lists of turples (y,x) that
        make a single region of points"""
    visited = set()   

    def enqueue_if_value(q,p):
        y,x = p
        if y < 0 or y >= rows or x < 0 or x >= cols:
            return
        if p in visited:
            return 
        if value_fn(p[0],p[1]) > 0:
            q.append(p)
            
    def expand_bag(p):
        bag = []
        q = deque()
        q.append(p)

        while len(q) > 0:
            p = q.popleft()           
            if p in visited:
                continue
            visited.add(p)
            y,x = p
            bag.append(p)
            
            enqueue_if_value(q,(y  ,x+1))
            enqueue_if_value(q,(y+1,x+1))
            enqueue_if_value(q,(y+1,x))
            enqueue_if_value(q,(y+1,x-1))
            enqueue_if_value(q,(y  ,x-1))
            enqueue_if_value(q,(y-1,x-1))
            enqueue_if_value(q,(y-1,x))
            enqueue_if_value(q,(y-1,x+1))
            
        return bag

    # processing loop starts here
    for y in range(0,rows):
        for x in range(0,cols):
            p = (y,x)
            if p not in visited:
                if value_fn(y,x) > 0:
                    yield expand_bag(p)
                else:
                    visited.add(p)

def find_regions(value_fn, cols, rows):
    """Walks the data via the value_fn such that every point in 0 -> cols & 0-> rows
        is visited by calling value_fn(y,x). Returns a list of lists of turples (y,x)"""
    bags = []
    for bag in iter_regions(value_fn, cols, rows):
        bags.append(bag)
    return bags
             

if __name__ == '__main__':
    data = [[0,0,0,0,0,1,0,0,0,0],
            [0,0,0,1,1,1,0,1,1,0],
            [0,0,0,1,0,1,0,0,0,1],
            [0,0,0,0,0,1,0,0,0,0]
            ]
    for bag in iter_regions(value_fn_from_array(data),len(data[0]), len(data)):
        print str(bag)
    