
import numpy as np

class Data_generator(object):
    
    def __init__(self,K,d,reward_type='binary'):
        
        self.d = d # dimension of the feature vector
        self.K = K # number of bandits
        self.reward_type = reward_type
        self.means = np.random.normal(size=self.K)
        self.stds = 1 + 2*np.random.rand(self.K)
        
        # generate the weight vectors
        self.generate_weight_vectors()
        
    def generate_weight_vectors(self,loc=0.0,scale=1.0):
        self.W = np.random.normal(loc=loc,scale=scale,size=(self.K,self.d))
        
    def generate_samples(self,n=1000):
        # the X are only binary
        X = np.random.randint(0,2,size=(n,self.d))
        # the rewards are functions of the inner products with self.W        
        IP = np.dot(X,self.W.T)
        # now get the rewards
        if self.reward_type == 'binary':
            R = (np.sign(np.random.normal(self.means + IP,self.stds)) + 1) / 2
        elif self.reward_type == 'positive':
            R = np.random.lognormal(self.means + IP,self.stds)
        elif self.reward_type == 'mixed':
            R = (np.sign(np.random.normal(self.means + IP,self.stds)) + 1) / 2
            R *= np.random.lognormal(self.means + IP,self.stds)
        return X,R