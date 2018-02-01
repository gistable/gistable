class Class:
    pass

def say_hello(self):
    print "Hello"

Class.say_hello = say_hello

Class().say_hello()