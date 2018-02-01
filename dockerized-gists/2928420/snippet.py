
# Back-Propagation Neural Networks
# 
# Written in Python.  See http://www.python.org/
# Modified by JSun to solve the problem here: http://www.weibo.com/1497035431/ynPEvC78V
# Neil Schemenauer <nas@arctrix.com>

import math
import random
import string

random.seed(0)

# calculate a random number where:  a <= rand < b
def rand(a, b):
    return (b-a)*random.random() + a

# Make a matrix (we could use NumPy to speed this up)
def makeMatrix(I, J, fill=0.0):
    m = []
    for i in range(I):
        m.append([fill]*J)
    return m

# our sigmoid function, tanh is a little nicer than the standard 1/(1+e^-x)
def sigmoid(x):
    return math.tanh(x)

# derivative of our sigmoid function, in terms of the output (i.e. y)
def dsigmoid(y):
    return 1.0 - y**2

def argmax(L):
    idx_max = -1
    v_max = 0
    for i,x in enumerate(L):
        if idx_max == -1:
            v_max = x
            idx_max = i
        if x>v_max:
            idx_max = i
            v_max =x
    return idx_max

class NN:
    def __init__(self, ni, nh, no):
        # number of input, hidden, and output nodes
        self.ni = ni + 1 # +1 for bias node
        self.nh = nh
        self.no = no

        # activations for nodes
        self.ai = [1.0]*self.ni
        self.ah = [1.0]*self.nh
        self.ao = [1.0]*self.no
        
        # create weights
        self.wi = makeMatrix(self.ni, self.nh)
        self.wo = makeMatrix(self.nh, self.no)
        # set them to random vaules
        for i in range(self.ni):
            for j in range(self.nh):
                self.wi[i][j] = rand(-0.2, 0.2)
        for j in range(self.nh):
            for k in range(self.no):
                self.wo[j][k] = rand(-2.0, 2.0)

        # last change in weights for momentum   
        self.ci = makeMatrix(self.ni, self.nh)
        self.co = makeMatrix(self.nh, self.no)

    def update(self, inputs):
        if len(inputs) != self.ni-1:
            raise ValueError('wrong number of inputs')

        # input activations
        for i in range(self.ni-1):
            #self.ai[i] = sigmoid(inputs[i])
            self.ai[i] = inputs[i]

        # hidden activations
        for j in range(self.nh):
            sum = 0.0
            for i in range(self.ni):
                sum = sum + self.ai[i] * self.wi[i][j]
            self.ah[j] = sigmoid(sum)

        # output activations
        for k in range(self.no):
            sum = 0.0
            for j in range(self.nh):
                sum = sum + self.ah[j] * self.wo[j][k]
            self.ao[k] = sigmoid(sum)
            #self.ao[k] = sum

        return self.ao[:]


    def backPropagate(self, targets, N, M):
        if len(targets) != self.no:
            raise ValueError('wrong number of target values')

        # calculate error terms for output
        output_deltas = [0.0] * self.no
        for k in range(self.no):
            error = targets[k]-self.ao[k]
            output_deltas[k] = dsigmoid(self.ao[k]) * error
            #output_deltas[k] = error

        # calculate error terms for hidden
        hidden_deltas = [0.0] * self.nh
        for j in range(self.nh):
            error = 0.0
            for k in range(self.no):
                error = error + output_deltas[k]*self.wo[j][k]
            hidden_deltas[j] = dsigmoid(self.ah[j]) * error

        # update output weights
        for j in range(self.nh):
            for k in range(self.no):
                change = output_deltas[k]*self.ah[j]
                self.wo[j][k] = self.wo[j][k] + N*change + M*self.co[j][k]
                self.co[j][k] = change
                #print N*change, M*self.co[j][k]

        # update input weights
        for i in range(self.ni):
            for j in range(self.nh):
                change = hidden_deltas[j]*self.ai[i]
                self.wi[i][j] = self.wi[i][j] + N*change + M*self.ci[i][j]
                self.ci[i][j] = change

        # calculate error
        error = 0.0
        for k in range(len(targets)):
            error = error + 0.5*(targets[k]-self.ao[k])**2
        return error

    
    def test(self, patterns):
        result = []
        for p in patterns:
            ttt = self.update(p[0])
            result.append(argmax(ttt))
        return result

    def weights(self):
        print('Input weights:')
        for i in range(self.ni):
            print(self.wi[i])
        print()
        print('Output weights:')
        for j in range(self.nh):
            print(self.wo[j])

    def train(self, patterns, iterations=3000, N=0.05, M=0.001):
        # N: learning rate
        # M: momentum factor
        for i in range(iterations):
            error = 0.0
            for p in patterns:
                inputs = p[0]
                targets = p[1]
                self.update(inputs)
                error = error + self.backPropagate(targets, N, M)
            if i % 100 == 0:
                print('error %-.5f' % error)


def demo():
    # Teach network XOR function
    pat = [
        [[0,0], [0]],
        [[0,1], [1]],
        [[1,0], [1]],
        [[1,1], [0]]
    ]

    # create a network with two input, two hidden, and one output nodes
    n = NN(2, 2, 1)
    # train it with some patterns
    n.train(pat)
    # test it
    print n.test(pat)
    
def R(n):
        t = []
        for i in range(10):
            if i==n:
                t.append(1)
            else:
                t.append(0)
        return t
def Q(L):
    H = [0]*10
    for x in L:
        H[x]+=1
    return H

def demo_digit():
    pat = [
        [Q([7,1,1,1]), R(0)],
        [Q([8,8,0,9]), R(6)],
        [Q([2,1,7,2]), R(0)],
        [Q([6,6,6,6]), R(4)],
        [Q([1,1,1,1]), R(0)],
        [Q([2,2,2,2]), R(0)],
        [Q([7,6,6,2]), R(2)],
        [Q([9,3,1,3]), R(1)],
        [Q([0,0,0,0]), R(4)],
        [Q([5,5,5,5]), R(0)],
        [Q([8,1,9,3]), R(3)],
        [Q([8,0,9,6]), R(5)],
        [Q([4,3,9,8]), R(3)],
        [Q([9,4,7,5]), R(1)],
        [Q([9,0,3,8]), R(4)],
        [Q([3,1,4,8]), R(2)]
    ]

    # create a network with two input, two hidden, and one output nodes
    n = NN(10, 10, 10)
    # train it with some patterns
    n.train(pat)
    # test it
    #tt = [ [Q([2,8,8,9]),[0]*10] ]
    tt = pat
    print n.test(tt)
    
    tt = [ [Q([2,8,8,9]),[0]*10] ]
    print n.test(tt)

if __name__ == '__main__':
    demo_digit()
