class globalizer():
    def __init__(self):
        global a
        a = self #global self formbidden bcs self is an ARGUMENT

cloud = globalizer()

if __name__ == '__main__':
    cloud.nbr = 1
    cloud.string = 'Hello World'
    
    def randFunction():
        for i in range(cloud.nbr):
            print(cloud.string)
    
    randFunction()
            
            

    