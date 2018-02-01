import string

class MyCoder(object):
    def __init__(self):
        self.letters = string.ascii_uppercase

    def encode(self,msg,skip):
        return "".join([self.letters[abs(len(self.letters) - self.letters.index(x) - skip)] for x in msg.upper()])

    def decode(self,msg,skip):
        return "".join([self.letters[abs(len(self.letters) - (self.letters.index(x) + skip))] for x in msg.upper()])

mycoder = MyCoder()
print(mycoder.encode("DAMIAN", 2))
print(mycoder.decode("VYMQYL", 2))