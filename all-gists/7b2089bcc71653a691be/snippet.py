class F:
    
    def __init__(self):
        self.cache = {}
        
    def __call__(self, n):
        if n in self.cache.keys():
            return self.cache[n]
        else:
            if n == 1:
                return 1
            else:
                return n*self.__call__(n-1)
            
factorial = F()
factorial(4)