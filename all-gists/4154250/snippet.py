"""
How to use:
1. Place a "Python Script" node on your canvas
2. Hook your "Classification Tree" node out into the "Python Script" input
3. Paste this gist in the python script and hit "Execute"

The output should be similar to this:

    # slope (<32.000, 34.000>) 
    if slope <=1.008: return False #(<7.000, 0.000>)  
    if slope >1.008: 
        # peak_i (<25.000, 34.000>) 
        if peak_i <=39.500: return False #(<19.000, 2.000>)  
        if peak_i >39.500: return True #(<6.000, 32.000>) 


Based on http://orange.biolab.si/doc/reference/Orange.classification.tree/#tree-structure
"""

def print_tree0(node, level):
    if not node:
        print " "*level + "<null node>"
        return
    if node.branch_selector:
        node_desc = node.branch_selector.class_var.name
        node_cont = node.distribution
        indent = "    " * level
        print "\n" + indent + "# %s (%s)" % (node_desc, node_cont),
        for i in range(len(node.branches)):
            print "\n{indent}if {var} {op}:".format(indent=indent, var=node_desc, op=node.branch_descriptions[i]),
            print_tree0(node.branches[i], level+1)
    else:
        node_cont = node.distribution
        major_class = node.node_classifier.default_value
        print "return %s #(%s) " % (major_class, node_cont),

print_tree0(in_classifier.tree, 0)