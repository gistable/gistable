import numpy as np
import cv2

# cellular automata class based on code from http://www.loria.fr/~rougier/teaching/numpy/scripts/game-of-life-numpy.py
class CA(object):
    def __init__(self, s, b, shape, init_fill=0.1):
        assert(type(s) == type([]) and type(b) == type([]))
        self.s,self.b = s,b
        self.z = (np.random.random(shape) < init_fill).astype("uint8")

    def __call__(self):
        N = (self.z[0:-2,0:-2] + self.z[0:-2,1:-1] + self.z[0:-2,2:] +
             self.z[1:-1,0:-2]                     + self.z[1:-1,2:] +
             self.z[2:  ,0:-2] + self.z[2:  ,1:-1] + self.z[2:  ,2:])

        # Apply rules
        tmp = None
        for b in self.b:
            if tmp is None:
                tmp = "((N==%d)"%b
            else:
                tmp += "|(N==%d)"%b
        tmp += ") & (self.z[1:-1,1:-1]==0)"
        birth = eval(tmp)
        tmp = None
        for s in self.s:
            if tmp is None:
                tmp = "((N==%d)"%s
            else:
                tmp += "|(N==%d)"%s
        tmp += ") & (self.z[1:-1,1:-1]==1)"
        survive = eval(tmp)
        self.z[...] = 0
        self.z[1:-1,1:-1][birth | survive] = 1

    def add_noise(self, amount=0.1):
        if amount == 0.:
            return
        n = np.random.random(self.z.shape) < amount
        self.z[n] = 1

    def show(self,scale=(1,1)):
        cv2.imshow("CA", cv2.resize(self.z*255, (self.z.shape[0]*scale[0],self.z.shape[1]*scale[1])))
        cv2.waitKey(5)

if __name__ == '__main__':
    # mazectric ruleset B3/S1234
    # 100 x 80 cell maze
    # initial chance of a cell being on is 80%. Higher numbers tend to converge more quickly
    c = CA([1,2,3,4],[3],(100,80),0.8)
    # scale the output by 5x so it's easier to see
    scl = (5,5)
    c.show(scl)
    # 20 outer iterations
    #   iterate 100 times then introduce some noise to try and unstick cycles
    for i in range(20):
        for i in range(100):
            c()
        c.show(scl)
        # add less noise each outer iteration until the last where there's no noise
        c.add_noise(0.5 - ((i+1)/20.)*0.5)
    # one final set of 100 iterations to clear up any remaining noise
    for i in range(100):
        c()
    # hit a key to exit
    cv2.waitKey(0)
