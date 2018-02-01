import unittest

class Test1 (unittest.TestCase): #Define a class which extend unittest
        def runTest(self):
        self.failIf (1+1 != 2, '1+1 failed !')

def suite():
        suite = unittest.TestSuite() #create an object testsuite
        suite.addTest(Test1())
        return suite

if __name__ == '__main__':
        runner = unittest.TextTestRunner() #Declare the runner
        test_suite = suite()
        runner.run(test_suite)
