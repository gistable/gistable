import unittest

# Here's our "unit".
def IsOdd(n):
    return n % 2 == 1

def IsaString(text):
	#text = "Hello"
	text = ['apples', 'bananas']
	return type(text)


# Here's our "unit tests".
class IsOddTests(unittest.TestCase):

    def testOne(self):
        self.failUnless(IsOdd(1))

    def testTwo(self):
        self.failIf(IsOdd(2))

'''
class IsaStringTests(unittest.TestCase):
	def testOne(self):
		self.failUnless(IsaString(str))
	def testTwo(self):
		self.failIf(IsaString(list))
'''
class IsaStringTests(unittest.TestCase):
	def testOne(self):
		self.failUnless(not IsaString(str))

def main():
    unittest.main()

if __name__ == '__main__':
    main()