#!/usr/bin/python3

# This can either be run from a command line with python3 alphabeta.py or imported with
# from alphabeta import alphabeta

# USAGE:
# alphabeta(input, start, lower, upper)
#
# Where:
# input is a list form input tree.  See example in this file.
# start is the root node number.  So, either 0 or 1 (0 if root is MAX, 1 if root is MIN)
# upper is the upper limit for beta.  Set this to something higher than any value in your tree
# lower is the lower limit for alpha.  Set this to something less than any value in your tree
#
# The function returns the root alpha and beta values, as well as the result, and the number of
# 'prunings' that took place.

# This is the tree we are working with
tree = [[[5, 1, 2], [8, -8, -9]], [[9, 4, 5], [-3, 4, 3]]]
root = 0
pruned = 0

def children(branch, depth, alpha, beta):
    global tree
    global root
    global pruned
    i = 0
    for child in branch:
        if type(child) is list:
            (nalpha, nbeta) = children(child, depth + 1, alpha, beta)
            if depth % 2 == 1:
                beta = nalpha if nalpha < beta else beta
            else:
                alpha = nbeta if nbeta > alpha else alpha
            branch[i] = alpha if depth % 2 == 0 else beta
            i += 1
        else:
            if depth % 2 == 0 and alpha < child:
                alpha = child
            if depth % 2 == 1 and beta > child:
                beta = child
            if alpha >= beta:
                pruned += 1
                break
    if depth == root:
        tree = alpha if root == 0 else beta
    return (alpha, beta)

def alphabeta(in_tree=tree, start=root, lower=-15, upper=15):
    global tree
    global pruned
    global root

    (alpha, beta) = children(tree, start, lower, upper)
    
    if __name__ == "__main__":
        print ("(alpha, beta): ", alpha, beta)
        print ("Result: ", tree)
        print ("Times pruned: ", pruned)

    return (alpha, beta, tree, pruned)

if __name__ == "__main__":
    alphabeta()
