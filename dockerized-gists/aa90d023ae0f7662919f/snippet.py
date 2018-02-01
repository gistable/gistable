"""
MIT License

Copyright (c) 2016 Michael Shihrer (michael@shihrer.me)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
EXAMPLE USAGE: https://repl.it/NfZq/1

blocks = []
blocks.append(Block((21,10)))
blocks.append(Block((5,10)))
blocks.append(Block((5,10)))
blocks.append(Block((7,13)))
blocks.append(Block((2,4)))
pack = Packer()
pack.fit(blocks)

for block in blocks:
  if block.fit:
    print("size: {} loc: {}".format(block.size, block.fit.location))
  else:
    print("not fit: {}".format(block.size))
"""

"""
For a more fleshed out example, see: https://github.com/shihrer/BinPacker/tree/Develop

This has a number of optimizations like removing recursion so it can run on much,
much large inputs without hitting any stack limitations.  Basically an order of 
magnitude faster on very large inputs.  Also includes a simple visualizer for the results
using pygame.
"""

class Packer:
    """
    Defines a packer object to be used on a list of blocks.
    """
    def __init__(self):
        self.root = None

    def fit(self, blocks):
        """
        Initiates the packing.
            blocks: A list of block objects with a 'size' proprety representing (w,h) as a tuple.
        """
        self.root = Node((0, 0), blocks[0].size)

        for block in blocks:
            some_node = self.find_node(self.root, block.size)
            if some_node is not None:
                block.fit = self.split_node(some_node, block.size)
            else:
                block.fit = self.grow_node(block.size)

        return None

    def find_node(self, some_node, size):
        if some_node.used:
            return self.find_node(some_node.right, size) or self.find_node(some_node.down, size)
        elif (size[0] <= some_node.size[0]) and (size[1] <= some_node.size[1]):
            return some_node
        else:
            return None

    def split_node(self, some_node, size):
        some_node.used = True
        some_node.down = Node((some_node.location[0], some_node.location[1] + size[1]),
                              (some_node.size[0], some_node.size[1] - size[1]))
        some_node.right = Node((some_node.location[0] + size[0], some_node.location[1]),
                               (some_node.size[0] - size[0], size[1]))
        return some_node

    def grow_node(self, size):
        can_go_down = size[0] <= self.root.size[0]
        can_go_right = size[1] <= self.root.size[1]

        should_go_down = can_go_down and (self.root.size[0] >= (self.root.size[1] + size[1]))
        should_go_right = can_go_right and (self.root.size[1] >= (self.root.size[0] + size[0]))

        if should_go_right:
            return self.grow_right(size)
        elif should_go_down:
            return self.grow_down(size)
        elif can_go_right:
            return self.grow_right(size)
        elif can_go_down:
            return self.grow_down(size)
        else:
            return None

    def grow_right(self, size):
        new_root = Node((0, 0), (self.root.size[0] + size[0], self.root.size[1]))
        new_root.used = True
        new_root.down = self.root
        new_root.right = Node((self.root.size[0], 0), (size[0], self.root.size[1]))

        self.root = new_root

        some_node = self.find_node(self.root, size)
        if some_node is not None:
            return self.split_node(some_node, size)
        else:
            return None

    def grow_down(self, size):
        new_root = Node((0, 0), (self.root.size[0], self.root.size[1] + size[1]))
        new_root.used = True
        new_root.down = Node((0, self.root.size[1]), (self.root.size[0], size[1]))
        new_root.right = self.root

        self.root = new_root

        some_node = self.find_node(self.root, size)
        if some_node is not None:
            return self.split_node(some_node, size)
        else:
            return None

class Block:
    """
    Defines an object Block with two properties.
        size: tuple representing the blocks size (w,h)
         fit: Stores a Node object for output.
    """
    def __init__(self, size):
        self.size = size
        self.fit = None

class Node:
    """
    Defines an object Node for use in the packer function.  Represents the space that a block is placed.
        used: Boolean to determine if a node has been used.
        down: A node located beneath the current node.
        right: A node located to the right of the current node.
        size: A tuple (w,h) representing the size of the node.
        location: A tuple representing the (x,y) coordinate of the top left of the node.
    """
    def __init__(self, location, size):
        self.used = False
        self.down = None
        self.right = None
        self.size = size
        self.location = location
