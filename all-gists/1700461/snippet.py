#! /usr/bin/python 

import unittest

class Trie(object):
    """ Trie implementation in python 
    """
    
    def __init__(self, ):
        """ So we use a dictionary at each level to represent a level in the hashmap
        the key of the hashmap is the character and the value is another hashmap 
        
        """

        self.node = {}



    def build(self, str):
        """
        Takes a str and splits it character wise 
        Arguments:
        - `str`: The string to be stored in the trie
        """
        node = self.node
        for ch in str:
            if node.has_key(ch) is True:
                node = node[ch]
            else :
                node[ch] = {}
                node = node[ch]

    def search(self, str):
        node = self.node
        for ch in str:
            if node.has_key(ch) is True:
                node = node[ch]
            else :
                return False
        return True

class TrieTest(unittest.TestCase):
    """ Test case for the above trie data structure
    """
    
    def setUp(self):
        self.trie = Trie()
        self.trie.build('aditya')

    def testSearch(self):
        self.assertTrue(self.trie.search('aditya'))
        
    def testSearchFail(self):
        self.assertFalse(self.trie.search('adityasar'))

    def testPrefixSearch(self):
        self.assertTrue(self.trie.search('adi'))
    
    def suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TrieTest))
        return suite
        


if __name__ == '__main__':
   # unittest.TextTestRunner(verbosity=2).run(suite())
    unittest.main()
            
        
        

        
        
