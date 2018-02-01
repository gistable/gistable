class RunningStat(object):
    """ 
    Based on ideas presented in
    1. Numerically Stable, Single-Pass, Parallel Statistics Algorithms - http://www.janinebennett.org/index_files/ParallelStatisticsAlgorithms.pdf
    2. Accurately computing running variance - http://www.johndcook.com/standard_deviation.html 
    """ 
    
    def __init__(self):
        self.m_n = 0
        self.m_oldM = 0
        self.m_oldS = 0
        self.m_newM = 0
        self.m_newS = 0
        self.idenity = 1
        
    def clear(self):
        self.m_n = 0
        self.m_oldM = 0
        self.m_oldS = 0
        self.m_newM = 0
        self.m_newS = 0
        self.idenity = 1

    def size(self):
        return self.m_n
    
    def debug(self):
        return {"m_n":self.m_n,
        "m_oldM":self.m_oldM,
        "m_oldS":self.m_oldS,
        "m_newM":self.m_newM,
        "m_newS":self.m_newS,
        "variance":self.variance(),
        "mean":self.mean(),
        "std":self.std()}
        
    def push(self,x):
        self.m_n = self.m_n + 1
        self.idenity = 0
        
        if self.m_n == 1:
            self.m_oldM = x
            self.m_newM = x
            self.m_oldS = 0        
        else:
            self.m_newM = self.m_oldM + (x - self.m_oldM) / self.m_n
            self.m_newS = self.m_oldS + (x - self.m_oldM)*(x - self.m_newM)
            
            self.m_oldM = self.m_newM 
            self.m_oldS = self.m_newS
            
    def mean(self):
        if self.m_n < 0:
            return 0
        else:
            return self.m_newM
        
    def variance(self):
        if self.m_n < 1:
            return 0
        else:
            return self.m_newS / (self.m_n - 1)
        
    def std(self):
        from numpy import sqrt
        return sqrt(self.variance())  
    
    def __add__(self,right):
        if type(right) is not RunningStat:
            raise TypeError('unsupported operand type(s) for +'+
                            ': \''+ str(type(self))[17:-2] +'\' and \''+ str(type(right)) +'\'') 
            
            
        c = RunningStat()
        
        if self.idenity == 1 and right.idenity == 0:
            return right

        elif self.idenity  == 0 and right.idenity == 1:
            return self

        
        
        else:
            m1 = self.mean() 
            n1 = self.size()
            d1 = self.m_newS

            m2 = right.mean()
            n2 = right.size()
            d2 = right.m_newS

            delta = (m2 - m1)
            delta2 = delta * delta

            c.m_n = n1 + n2 
            if c.m_n == 0:
                return right
            
            c.m_oldM = m1 + n2*(delta/(c.m_n))
            c.m_newM = m1 + n2*(delta/(c.m_n)) 
            
            
            q = (n1 * n2) * (delta2 / c.m_n)
            c.m_oldS = d1 + d2 + q
            c.m_newS = d1 + d2 + q
            
            c.idenity = 0

            return c

def get_rolling_stats(list_of_values):
    accumaltor = RunningStat()
    for i in list_of_values:
        accumaltor.push(i)
    return accumaltor

def aggrate_rolling_values(list_of_rs):
    i = list_of_rs[0]
    for r in list_of_rs[1:]:
        i = i + r
    return i




def test_suit():
    from math import fabs
    import numpy as np
    
    error = 0.0000001 
    
    # Setup test data
    
    t1 = np.random.randint(9, size=(1,2000)) * 8.9
    t1 = list(t1[0])


    t2 = np.random.randint(20, size=(1,200)) * 8.9
    t2 = list(t2[0])


    t3 = np.random.randint(100, size=(1,500)) * 8.9
    t3 = list(t3[0])

    t4 = t1 + t2 + t3 



    # crate instances of data structure 
    h1 = get_rolling_stats(t1)
    h2 = get_rolling_stats(t2)
    h3 = get_rolling_stats(t3)

    h_1_2 = get_rolling_stats(t1 + t2)
    h4 = get_rolling_stats(t4)

    # Test map opperation and addition
    l_rs = [h1,h2,h3]
    h5 = aggrate_rolling_values(l_rs)

    # Test addition 
    h6 = (h1 + h2) + h3

    
    # The true values are dervied from numpy
    
    # True variances for h1,h2,h3
    x1 = np.var(t1,ddof=1)
    x2 = np.var(t2,ddof=1)
    x3 = np.var(t3,ddof=1)
    
    # True means for h1,h2,h3

    y1 = np.mean(t1)
    y2 = np.mean(t2)
    y3 = np.mean(t3)
    
    # True std for h1,h2,h3
    z1 = np.std(t1,ddof=1)
    z2 = np.std(t2,ddof=1)
    z3 = np.std(t3,ddof=1)
    
    
    # True mean and variances and std for h_1_2
    
    x_1_2 = np.var(t1 + t2,ddof=1)
    y_1_2 = np.mean(t1 + t2)
    z_1_2 = np.std(t1 + t2,ddof=1)

    
    # True mean and variances for h4 
    x4 = np.var(t4,ddof=1)
    y4 = np.mean(t4)
    z4 = np.std(t4,ddof=1)



    assert fabs(h1.mean() - y1) <= error
    assert fabs(h1.variance() - x1) <= error
    assert fabs(h1.std() - z1) <= error
    assert h1.variance() > 0
    assert h1.std() > 0

    assert fabs(h2.mean() - y2) <= error 
    assert fabs(h2.variance() - x2) <= error
    assert fabs(h2.std() - z2) <= error
    assert h2.std() > 0
    assert h2.variance() > 0

    assert fabs(h3.mean() - y3) <= error
    assert fabs(h3.variance() - x3) <= error
    assert fabs(h3.std() - z3) <= error
    assert h3.std() > 0
    assert h3.variance() > 0

    assert fabs(h4.mean() - y4) <= error
    assert fabs(h4.variance() - x4) <= error
    assert fabs(h4.std() - z4) <= error
    assert h3.std() > 0
    assert h4.variance() > 0

    assert fabs(h_1_2.mean() - y_1_2) <= error
    assert fabs(h_1_2.variance() - x_1_2) <= error
    assert fabs(h_1_2.std() - z_1_2) <= error
    assert h_1_2.std() > 0
    assert h_1_2.variance() > 0

    assert fabs(h6.mean() - y4) <= error 
    assert fabs(h6.variance() - x4) <= error
    assert fabs(h6.std() - z4) <= error
    assert h6.std() > 0
    assert h6.variance() > 0

    assert fabs(h5.mean() - y4) <= error
    assert fabs(h5.variance() - x4) <= error
    assert fabs(h5.std() - z4) <= error
    assert h5.std() > 0 
    assert h5.variance() > 0
    
for i in range(0,1000):
    test_suit()
print "Testing Done" 