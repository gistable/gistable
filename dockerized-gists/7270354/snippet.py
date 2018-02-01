from numpy import *

class BLUE:
    """A simple implementation of BLUE for 2 measurements"""
 
    def __init__(self):
        self.values = matrix([0,0])
        self.ematrix = matrix([[0,0],[0,0]])

    def AddMeasurement(self,v1,v2):
        self.values = matrix([v1,v2])

    def AddUncertainty(self,e1,e2,corr):
        uncmatrix = matrix([[e1**2,e1*e2*corr],[e1*e2*corr,e2**2]])
        self.ematrix = self.ematrix + uncmatrix

    def Simple(self):
        print 'ematrix: \n', self.ematrix

        unitvector = matrix([1,1]).T
        self.weights = self.ematrix.I*unitvector/(unitvector.T*self.ematrix.I*unitvector)

        print 'weights: ', self.weights.T
        
        self.average = self.values*self.weights
        print 'average: ', self.average

        self.error = sqrt(self.weights.T*self.ematrix*self.weights)
        print 'error: ', self.error

        return [self.average,self.error]
