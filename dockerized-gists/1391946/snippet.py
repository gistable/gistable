class Node:
    def __init__(self):
        self.next = {}
        self.word_marker = False 


    def add(self, string):
        
        if len(string) == 0:
            self.word_marker = True 
            return 
        
        key = string[0] 
        string = string[1:] 

        if self.next.has_key(key):
            self.next[key].add(string)
        else:
            node = Node()
            self.next[key] = node
            node.add(string)


    def partial(self, sf=None):
        
        if self.next.keys() == []:
            print "Match:",sf
            return
            
        if self.word_marker == True:
            print "Match:",sf

        for key in self.next.keys():
            self.next[key].partial(sf+key)

    def search(self, string, sf=""):
        if len(string) > 0:
            key = string[0]
            string = string[1:]
            if self.next.has_key(key):
                sf = sf + key
                self.next[key].search(string,sf)
                
            else:
                print "No match"
        else:
            if self.word_marker == True:
                print "Match:",sf

            for key in self.next.keys():
                self.next[key].partial(sf+key)

    def exact_match(self, string, sf=''):
        if len(string) > 0:
            key = string[0]
            string = string[1:]
            if self.next.has_key(key):
                sf = sf + key
                self.next[key].exact_match(string,sf)
                
            else:
                print "No match"
        else:
            if self.word_marker == True:
                print "Match:",sf
            elif self.word_marker==False:
                print 'No Match.'

    def all_trie(self):
        a=sorted(self.next.keys())
        if(len(a)==0):
            print 'Empty Trie.'
        for b in a:
            self.next[b].partial(b)
