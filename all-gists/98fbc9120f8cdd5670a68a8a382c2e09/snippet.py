class Node(object):
    def __init__(self, data):
        self.data = data
        self.leftchild = None
        self.rightchild = None

    def insert(self,data):
        #all the heavy lifting stuff is done in the node class
        if(self.data == data):
            return False #we dont want any duplicates
        elif(self.data > data):
            if(self.leftchild):
                return self.leftchild.insert(data)
            else:
                self.leftchild = Node(data)
                return True
        else:
            if(self.rightchild):
                return self.rightchild.insert(data)
            else:
                self.rightchild = Node(data)
                return True

    def find(self,data):
        if(self.data == data):
            return True
        elif(self.data > data):
            if(self.leftchild):
                return self.leftchild.find(data)
            else:
                return False
        else:
            if(self.rightchild):
                return self.rightchild.find(data)
            else:
                return False

    def preorder(self):
        if(self):
            print(str(self.data))
            if(self.leftchild):
                self.leftchild.preorder()
            if(self.rightchild):
                self.rightchild.preorder()

    def inorder(self):
        if(self):
            if(self.leftchild):
                self.leftchild.inorder()
            print(str(self.data))
            if(self.rightchild):
                self.rightchild.inorder()

    def postorder(self):
        if(self):
            if(self.leftchild):
                self.leftchild.postorder()
            if(self.rightchild):
                self.rightchild.postorder()
            print(str(self.data))


class BSTree(object):
    def __init__(self):
        self.root = None

    def insert(self,data):
        if(self.root):
            return self.root.insert(data)
        else:
            self.root = Node(data)
            return True

    def lookup(self,data):
        if(self.root):
            return self.root.find(data)
        else:
            return False

    def delete(self,data):
        #if empty tree
        if(self.root == None):
            return False

        #if the data is in the root node
        elif(self.root.data == data):
            if(self.root.leftchild is None and self.root.rightchild is None):
                self.root = None
            elif(self.leftchild and self.rightchild is None):
                self.root = self.root.leftchild
            elif(self.leftchild is None and self.rightchild):
                self.root = self.root.rightchild
            elif(self.leftchild and self.rightchild):
                delnodeparent = self.root
                delnode = self.root.rightchild
                while delnode.leftchild:
                    delnodeparent = delnode
                    delnode = delnode.leftchild

                self.root.data = delnode.data
                if(delnode.rightchild):
                    if(delnodeparent.data > delnode.data):
                        delnodeparent.leftchild = delnode.rightchild
                    elif(delnodeparent.data < delnode.data):
                        delnodeparent.rightchild = delnode.rightchild
                else:
                    if(delnode.data < delnodeparent.data):
                        delnodeparent.leftchild = None
                    else:
                        delnodeparent.rightchild = None

        #if data is not in the root node
        parent = None
        node = self.root

        #find the node to remove
        while(node and node.data != data):
            parent = node
            if(data < node.data):
                node = node.leftchild
            elif(data > node.data):
                node = node.rightchild

        #case 1 : data is not found
        if(node is None or node.data != data):
            return False

        #case 2 : if remove-node has no children
        if(node.leftchild is None or node.rightchild is None):
            if(data < parent.data):
                parent.leftchild = None
            else:
                parent.rightchild = None
            return True

        #case 3 : remove-node has a left child only
        elif(node.leftchild and node.rightchild is None):
            if(data < parent.data):
                parent.leftchild = node.leftchild
            else:
                parent.rightchild = node.leftchild
            return True

        #case 4 : remove-node has a right child only
        elif(node.leftchild is None and node.rightchild):
            if(data < parent.data):
                parent.leftchild = node.rightchild
            else:
                parent.rightchild = node.rightchild
            return True

        #case 5 : remove-node has left and right children
        else:
            delnodeparent = node
            delnode = node.rightchild
            while delnode.leftchild:
                delnodeparent = delnode
                delnode = delnode.leftchild

            node.data = delnode.value
            if(delnode.rightchild):
                if(delnodeparent.data > delnode.data):
                    delnodeparent.leftchild = delnode.rightchild
                elif(delnodeparent.data < delnode.data):
                    delnodeparent.rightchild = delnode.rightchild
            else:
                if(delnode.data < delnodeparent.data):
                    delnodeparent.leftchild = None
                else:
                    delnodeparent.rightchild = None

    def print_tree(self):
        print("PreOrder Traversal")
        self.root.preorder()
        print("--------------")
        print("InOrder Traversal")
        self.root.inorder()
        print("--------------")
        print("PostOrder Traversal")
        self.root.postorder()



