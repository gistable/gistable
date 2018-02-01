import numpy as np

def gaussian(x0, sigma):
    return lambda x : np.exp(- 0.5 * ((x - x0) / sigma)**2 ) / (sigma * np.sqrt(2 * np.pi))

def kde(points, sigma=.5):
    functions = [gaussian(x0, sigma) for x0 in points]
    def sampler(x):
        return sum(f(x) for f in functions)
    return sampler
    
if __name__ == "__main__":
    points = [1, 3, 6, 3, 6, 2, 1, 4, 6]
    sampler = kde(points)
    print "unnormalized KDE @ x=5 => ", sampler(5)