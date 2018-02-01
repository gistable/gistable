import math

class Vector(object):
    def __init__(self, coordinates):
        try:
            if not coordinates:
                raise ValueError
            self.coordinates = tuple(coordinates)
            self.dimension = len(coordinates)

        except ValueError:
            raise ValueError('The coordinates must be nonempty')

        except TypeError:
            raise TypeError('The coordinates must be an iterable')


    def __str__(self):
        return 'Vector: {}'.format(self.coordinates)


    def __eq__(self, v):
        return self.coordinates == v.coordinates

    def __add__(self, v):
        try:
            if len(self.coordinates) != len(v.coordinates):
                raise ValueError
            return Vector([x+y for x,y in zip(self.coordinates, v.coordinates)])

        except ValueError:
            raise ValueError('Vectors are not in the same space')


    def __sub__(self, v):
        try:
            if len(self.coordinates) != len(v.coordinates):
                raise ValueError
            return Vector([x-y for x,y in zip(self.coordinates, v.coordinates)])

        except ValueError:
            raise ValueError('Vectors are not in the same space')

    def __mul__(self, v):
        try:
            if(type(v) is int or type(v) is float):
                return Vector([x*v for x in self.coordinates])
        
        except ValueError:
            raise ValueError('Vectors are not in the same space')
    
    def getMagnitude(self):
        return round(sum([c**2 for c in self.coordinates])**0.5, 3)

    def normalize(self):
        return self.__mul__(1/self.getMagnitude())

    def dot(self, v):
        return sum([x*y for x,y in zip(self.coordinates, v.coordinates)])

    def getAngleBetween(self, v, mode = 'rad'):
        radian = math.acos(self.normalize().dot(v.normalize()))
        if(mode == 'rad'):
            return radian
        else:
            return math.degrees(radian)

    def isZero(self, tolerance=1e-10):
        return self.getMagnitude() < tolerance

    def isOrthogonalTo(self, v, tolerance=1e-10):
        return abs(self.dot(v)) < tolerance
    
    def isParallelTo(self, v):
        return (self.isZero()
                or v.isZero()
                or self.getAngleBetween(v) == 0
                or self.getAngleBetween(v) == math.pi)

    def getParallelComponent(self, basis):
        unit_vector = basis.normalize()
        return  unit_vector.__mul__(self.dot(basis)/basis.getMagnitude())

    def getOrthogonalComponent(self, basis):
        return self.__sub__(self.getParallelComponent(basis))

v1 = Vector([3.039, 1.879])
v2 = Vector([0.825, 2.036])
print(v1)
print(v1.getParallelComponent(v2))
print(v1.getOrthogonalComponent(v2))
print(v1.getOrthogonalComponent(v2) + v1.getParallelComponent(v2))

        
