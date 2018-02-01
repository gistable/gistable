class Coordinate(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def getX(self):
        # Getter method for a Coordinate object's x coordinate.
        # Getter methods are better practice than just accessing an attribute directly
        return self.x

    def getY(self):
        # Getter method for a Coordinate object's y coordinate
        return self.y

    def __str__(self):
        return '<' + str(self.getX()) + ',' + str(self.getY()) + '>'

    def __eq__(self, other):
        # First make sure `other` is of the same type 
        assert type(other) == type(self)
        # Since `other` is the same type, test if coordinates are equal
        return self.getX() == other.getX() and self.getY() == other.getY()

    def __repr__(self):
        return 'Coordinate(' + str(self.getX()) + ',' + str(self.getY()) + ')'

a = Coordinate(2,3) # Create new object 'a'
b = Coordinate(4,5) # Create new object 'b'
print a.getX()      # Print the x value of object 'a'
print a.getY()      # Print the y value of object 'a'

print b == a        # Compare b with 'a'
print a == b        # Compare a with 'b'
                    # Notice how 'self' and 'other' are swapped during comparison,
                    # the left object gets assigned to self

print a             # How object 'a' is printed by __str__

print repr(a)       # How object 'a' is printed by __repr__ 
                    # Notice that the way it is printed, looks the same
                    # as object 'a' itself 'Coordinate(2,3)'.
                    # Using eval (python's built-in function), we 
                    # can evaluate the value of repr(a), hence the 
                    # example eval(repr(a)) == a

