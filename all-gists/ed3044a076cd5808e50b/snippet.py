class Human:
    age = 0
    name = '';
    
    def __init__(self, name, age):
        self.name = name
        self.age = age
        
    def setAge(self, age):
        self.age = age
        return self
        
    def setName(self, name):
        self.name = name
        return self
    
    def getAge(self):
        return self.age
    
    def getName(self):
        return self.name
    

if (__name__ == "__main__"):
    meysam = Human("Meysam", 25)
    
    print(meysam.getName(),"with",meysam.getAge(),"old.")
    
    meysam.setAge(23).setName("Saleh")
    
    print(meysam.getName(),"with",meysam.getAge(),"old.")