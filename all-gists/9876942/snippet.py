"""
  File name: gp_alter.py
  Author: Thomas Macrina
  Date created: 03/21/2014
  Python Version: 2.7

Overwriting the generate() method within DEAP's gp.py
to remove the need for "dummy" nodes within strongly-typed
individuals.

Starting at line 549, gp.py in v1.0.0
"""

def generate(pset, min_, max_, condition, type_=__type__):
    """Generate a Tree as a list of list. The tree is build
    from the root to the leaves, and it stop growing when the
    condition is fulfilled.

    :param pset: A primitive set from wich to select primitives of the trees.
    :param min_: Minimum height of the produced trees.
    :param max_: Maximum Height of the produced trees.
    :param condition: The condition is a function that takes two arguments,
                      the height of the tree to build and the current
                      depth in the tree.
    :param type_: The type that should return the tree when called, when
                  :obj:`None` (default) no return type is enforced.
    :returns: A grown tree with leaves at possibly different depths
              dependending on the condition function.
              
    
    DUMMY NODE ISSUES
    
    DEAP will only place terminals if we're at the bottom of a branch. 
    This creates two issues:
    1. A primitive that takes other primitives as inputs could be placed at the 
        second to last layer.
        SOLUTION: You need to allow the tree to end whenever the height condition is met,
                    so create "dummy" terminals for every type possible in the tree.
    2. A primitive that takes terminals as inputs could be placed above the second to 
        last layer.
        SOLUTION: You need to allow the tree to continue extending the branch until the
                    height condition is met, so create "dummy" primitives that just pass 
                    through the terminal types.
                    
    These "dummy" terminals and "dummy" primitives introduce unnecessary and sometimes 
    nonsensical solutions into populations. These "dummy" nodes can be eliminated
    if the height requirement is relaxed.    
    
    
    HOW TO PREVENT DUMMY NODE ISSUES
    
    Relaxing the height requirement:
    When at the bottom of the branch, check for terminals first, then primitives.
        When checking for primitives, skirt the height requirement by adjusting 
        the branch depth to be the second to last layer of the tree.
        If neither a terminal or primitive fits this node, then throw an error.
    When not at the bottom of the branch, check for primitives first, then terminals.
    
    Issue with relaxing the height requirement:
    1. Endless loops are possible when primitive sets have any type loops. 
        A primitive with an output of one type may not take an input type of 
        itself or a parent type.
        SOLUTION: A primitive set must be well-designed to prevent those type loops.
    
    """
    expr = []
    height = random.randint(min_, max_)
    stack = [(0, type_)]
    while len(stack) != 0:
        depth, type_ = stack.pop()
        # At the bottom of the tree
        if condition(height, depth):
            # Try finding a terminal
            try:
                term = random.choice(pset.terminals[type_])
                
                if isclass(term):
                    term = term()
                expr.append(term)                
            # No terminal fits
            except:
                # So pull the depth back one layer, and start looking for primitives
                try:
                    depth -= 1
                    prim = random.choice(pset.primitives[type_])
          
                    expr.append(prim)
                    for arg in reversed(prim.args):
                        stack.append((depth+1, arg)) 
                                    
                # No primitive fits, either - that's an error
                except IndexError:
                    _, _, traceback = sys.exc_info()
                    raise IndexError, "The gp.generate function tried to add "\
                                      "a primitive of type '%s', but there is "\
                                      "none available." % (type_,), traceback

        # Not at the bottom of the tree
        else:
            # Check for primitives
            try:
                prim = random.choice(pset.primitives[type_])
          
                expr.append(prim)
                for arg in reversed(prim.args):
                    stack.append((depth+1, arg))                 
            # No primitive fits
            except:                
                # So check for terminals
                try:
                    term = random.choice(pset.terminals[type_])
                
                # No terminal fits, either - that's an error
                except IndexError:
                    _, _, traceback = sys.exc_info()
                    raise IndexError, "The gp.generate function tried to add "\
                                      "a terminal of type '%s', but there is "\
                                      "none available." % (type_,), traceback
                if isclass(term):
                    term = term()
                expr.append(term)

    return expr
    