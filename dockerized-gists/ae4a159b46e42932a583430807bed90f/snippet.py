"""
Create a data structure that mimics Python's list.

IDEA: convert each element to a base representation with a fixed size (byte / binary / octal / hexadecimal ... etc)
	  then, concat elements as a string.
	  
Based on meetup: https://www.meetup.com/Deep-Dive-into-Python-Know-Thy-Interpreter/events/238587475/
"""

class List(object):

    def __init__(self, *args):
        self.body = ''
        self.size = 32
        for e in args:
            self.body += self._rep(e)

    def __contains__(self, element):
        for i in self._loop():
            if self._rep(element) == self._mem(i):
                return True
        return False

    def __repr__(self):
        l = '['
        for i in self._loop():
            l += self.to_actual(self._mem(i)) + ', '
        l += ']'
        return l.replace(', ]', ']')

    def _rep(self, e):
        return '{:032b}'.format(e)

    def index(self, e):
        for i in self._loop():
            if e == int(self.to_actual(self._mem(i))):
                return int(i / self.size)
        return None

    def append(self, e):
        self.body += self._rep(e)

    def pop(self):
        i = len(self.body) - self.size
        r = self.body[i:]
        self.body = self.body[:i]
        return self.to_actual(r)

    def remove(self, e):
        i = self.index(e)
        if i:
            i *= self.size
            self.body = self.body[:int(i)] + self.body[int(i + self.size):]

    def _mem(self, i):
        return self.body[i:i + self.size]

    def to_actual(self, raw):
        return str(int(raw, 2))

    def _loop(self):
        return range(0, len(self.body), self.size)


if __name__ == '__main__':

    mylist = List(3, 4, 3343432)
    mylist.append(34)
    print(mylist) 			# == mylist.__repr__()
    print(4 in mylist) 		# == mylist.__contains__(4)
    print(mylist.index(34))
    print(mylist.index(10))
    mylist.append(10)
    print(mylist.index(10))
    mylist.remove(4)
    print(mylist)
    print(mylist.pop())
    print(mylist)
    # out:
	    # [3, 4, 3343432, 34]
	    # True
	    # 3
	    # None
	    # 4
	    # [3, 3343432, 34, 10]
	    # 10
	    # [3, 3343432, 34]