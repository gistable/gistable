class SomeClass(object):
    x = 1
    y = 2
    
    def __init__(self, z):
        self.z = 0 # New attribute created
        delattr(self, 'z') # Attribute deleted--throws error if you try to access it
    
    def some_method(self):
        self.b = 1 # New attribute created