from math import sqrt


class Point:
    def __init__(self,x_init,y_init):
        self.x = x_init
        self.y = y_init

    def shift(self, x, y):
        self.x += x
        self.y += y

    def __repr__(self):
        return "".join(["Point(", str(self.x), ",", str(self.y), ")"])

p1 = Point(10, 3)
p2 = Point(1, 0)


def distance(a, b):
    return sqrt((a.x-b.x)**2+(a.y-b.y)**2)

print(p1.x, p1.y, p2.x, p2.y)
print(distance(p1,p2))

p2.shift(2,3)

print(p2)
