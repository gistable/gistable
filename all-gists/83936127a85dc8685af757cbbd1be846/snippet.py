__version__ = "1.0"

class Cat(object):
    def __init__(self):
        print "making cat"
        print "see?", type(self)
        self.name = "fluffy"

    def __add__(self, other):
        if not type(other) == Cat:
            raise "Go Away"
        kitten = Kitten()
        kitten.name = self.name + "-and-" + other.name
        return kitten

    def __eq__(self, other):
        return self.name == other.name



