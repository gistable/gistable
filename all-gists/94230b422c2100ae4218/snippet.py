#!/usr/bin/python3
# By Steve Hanov, 2011. Released to the public domain.
# Please see http://stevehanov.ca/blog/index.php?id=115 for the accompanying article.
#
# Based on Daciuk, Jan, et al. "Incremental construction of minimal acyclic finite-state automata." 
# Computational linguistics 26.1 (2000): 3-16.
#
# Updated 2014 to use DAWG as a mapping; see 
# Kowaltowski, T.; CL. Lucchesi (1993), "Applications of finite automata representing large vocabularies", 
# Software-Practice and Experience 1993
import sys
import time

DICTIONARY = "/usr/share/dict/words"
QUERY = sys.argv[1:]

# This class represents a node in the directed acyclic word graph (DAWG). It
# has a list of edges to other nodes. It has functions for testing whether it
# is equivalent to another node. Nodes are equivalent if they have identical
# edges, and each identical edge leads to identical states. The __hash__ and
# __eq__ functions allow it to be used as a key in a python dictionary.
class DawgNode:
    NextId = 0
    
    def __init__(self):
        self.id = DawgNode.NextId
        DawgNode.NextId += 1
        self.final = False
        self.edges = {}

        # Number of end nodes reachable from this one.
        self.count = 0

    def __str__(self):        
        arr = []
        if self.final: 
            arr.append("1")
        else:
            arr.append("0")

        for (label, node) in self.edges.items():
            arr.append( label )
            arr.append( str( node.id ) )

        return "_".join(arr)

    def __hash__(self):
        return self.__str__().__hash__()

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def numReachable(self):
        # if a count is already assigned, return it
        if self.count: return self.count

        # count the number of final nodes that are reachable from this one.
        # including self
        count = 0
        if self.final: count += 1
        for label, node in self.edges.items():
            count += node.numReachable()

        self.count = count
        return count

class Dawg:
    def __init__(self):
        self.previousWord = ""
        self.root = DawgNode()

        # Here is a list of nodes that have not been checked for duplication.
        self.uncheckedNodes = []

        # Here is a list of unique nodes that have been checked for
        # duplication.
        self.minimizedNodes = {}

        # Here is the data associated with all the nodes
        self.data = []

    def insert( self, word, data ):
        if word <= self.previousWord:
            raise Exception("Error: Words must be inserted in alphabetical " +
                "order.")

        # find common prefix between word and previous word
        commonPrefix = 0
        for i in range( min( len( word ), len( self.previousWord ) ) ):
            if word[i] != self.previousWord[i]: break
            commonPrefix += 1

        # Check the uncheckedNodes for redundant nodes, proceeding from last
        # one down to the common prefix size. Then truncate the list at that
        # point.
        self._minimize( commonPrefix )

        self.data.append(data)

        # add the suffix, starting from the correct node mid-way through the
        # graph
        if len(self.uncheckedNodes) == 0:
            node = self.root
        else:
            node = self.uncheckedNodes[-1][2]

        for letter in word[commonPrefix:]:
            nextNode = DawgNode()
            node.edges[letter] = nextNode
            self.uncheckedNodes.append( (node, letter, nextNode) )
            node = nextNode

        node.final = True
        self.previousWord = word

    def finish( self ):
        # minimize all uncheckedNodes
        self._minimize( 0 );

        # go through entire structure and assign the counts to each node.
        self.root.numReachable()

    def _minimize( self, downTo ):
        # proceed from the leaf up to a certain point
        for i in range( len(self.uncheckedNodes) - 1, downTo - 1, -1 ):
            (parent, letter, child) = self.uncheckedNodes[i];
            if child in self.minimizedNodes:
                # replace the child with the previously encountered one
                parent.edges[letter] = self.minimizedNodes[child]
            else:
                # add the state to the minimized nodes.
                self.minimizedNodes[child] = child;
            self.uncheckedNodes.pop()

    def lookup( self, word ):
        node = self.root
        skipped = 0 # keep track of number of final nodes that we skipped
        for letter in word:
            if letter not in node.edges: return None
            for label, child in sorted(node.edges.items()):
                if label == letter: 
                    if node.final: skipped += 1
                    node = child
                    break
                skipped += child.count

        if node.final:
            return self.data[skipped]

    def nodeCount( self ):
        return len(self.minimizedNodes)

    def edgeCount( self ):
        count = 0
        for node in self.minimizedNodes:
            count += len(node.edges)
        return count

    def display(self):
        stack = [self.root]
        done = set()
        while stack:
            node = stack.pop()
            if node.id in done: continue
            done.add(node.id)
            print("{}: ({})".format(node.id, node))
            for label, child in node.edges.items():
                print("    {} goto {}".format(label, child.id))
                stack.append(child)

if 0:
    dawg = Dawg()
    dawg.insert("cat", 0)
    dawg.insert("catnip", 1)
    dawg.insert("zcatnip", 2)
    dawg.finish()
    dawg.display()
    sys.exit()
            
dawg = Dawg()
WordCount = 0
words = open(DICTIONARY, "rt").read().split()
words.sort()
start = time.time()    
for word in words:
    WordCount += 1
    # insert all words, using the reversed version as the data associated with
    # it
    dawg.insert(word, ''.join(reversed(word)))
    if ( WordCount % 100 ) == 0: print("{0}\r".format(WordCount), end="")
dawg.finish()
print("Dawg creation took {0} s".format(time.time()-start))

EdgeCount = dawg.edgeCount()
print("Read {0} words into {1} nodes and {2} edges".format(
    WordCount, dawg.nodeCount(), EdgeCount))

print("This could be stored in as little as {0} bytes".format(EdgeCount * 4))

for word in QUERY:
    result = dawg.lookup(word)
    if result == None:
        print("{0} not in dictionary.".format(word))
    else:
        print("{0} is in the dictionary and has data {1}".format(word, result))