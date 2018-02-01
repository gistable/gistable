class Architects:
    def __init__(self, n, constraints):
        self.constraints = constraints
        self.n = n

    def size(self):
        return len(self.constraints[0])

    def north(self):
        return self.constraints[0]

    def south(self):
        return self.constraints[1]

    def west(self):
        return self.constraints[2]

    def east(self):
        return self.constraints[3]

    def viable(self, cs, p, todo=None):
        if todo is None:
            todo = []
        if not self.viable1(cs, p, True, todo):
            return False
        if not self.viable1(cs, p, False, todo):
            return False
        return True

    def viable1(self, cs, p, b, todo):
        if not self.isPermutation(cs, p, b):
            return False

        if b:
            side1 = self.west()[p.x]
            side2 = self.east()[p.x]
        else:
            side1 = self.north()[p.y]
            side2 = self.south()[p.y]

        if not self.visible(side1, cs, p, b, True):
            return False
        if not self.visible(side2, cs, p, b, False):
            return False
        return True

    def isPermutation(self, cs, p, b):
        n = self.size()
        aux = [False] * n
        for j in range(n):
            q = Pos(p.x, p.y).init(n, p, j, b)
            if cs.isDefined(q):
                a = cs.get(q)
                assert (0 < a <= n);
                if aux[a - 1]:
                    return False
                else:
                    aux[a - 1] = True
        return True

    def visible(self, expected, cs, p, b, side):
        if 0 == expected:
            return True
        n = self.size()
        max1 = 0
        max2 = 0
        result1 = 0
        result2 = 0
        a = 0
        for j in range(n):
            q = Pos(p.x, p.y).init(n, p, j, b, side)
            if cs.isDefined(q):
                a = cs.get(q)
                if a > max1:
                    max1 = a
                    result1 += 1
                if a > max2:
                    max2 = a
                    result2 += 1
            else:
                a = max(cs.getPossibilities(q))
                if a > max1:
                    max1 = n
                    result1 += 1
                if a > max2:
                    max2 += 1
                    result2 += 1
        return (result1 <= expected) and (expected <= result2)


class State:
    def __init__(self, n):
        self.size = n
        self.allPossibilities = []
        for h in range(1, n + 1):
            self.allPossibilities.append(h)

        self.decisionNodes = 0
        self.terrain = [[0] * n for i in range(n)]

    def isDefined(self, p):
        return self.terrain[p.x][p.y] != 0

    def selectUndefinedPos(self):
        self.decisionNodes += 1
        for i in range(self.size):
            for j in range(self.size):
                p = Pos(i, j)
                if not self.isDefined(p):
                    return p
        return None

    def get(self, p):
        if self.isDefined(p):
            return self.terrain[p.x][p.y]

    def set(self, p, h):
        if not self.isDefined(p):
            self.terrain[p.x][p.y] = h

    def unset(self, p):
        if self.isDefined(p):
            self.terrain[p.x][p.y] = 0

    def getPossibilities(self, p):
        return self.allPossibilities

class SmartState(State):
    def __init__(self, n):
        State.__init__(self, n)



class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def init(self, n, p, j, b, side=True):
        if b:
            if side:
                self.x = p.x
                self.y = j
            else:
                self.x = p.x
                self.y = n - j - 1
        else:
            if side:
                self.x = j
                self.y = p.y
            else:
                self.x = n - j - 1
                self.y = p.y
        return self

    def __hash__(self):
        return (((self.x + self.y) * (self.x + self.y + 1)) / 2) + self.x

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return (self.x == other.x) and (self.y == other.y)
        return NotImplemented


class EarlyChecks:
    def __init__(self, archi):
        self.archi = archi
        self.state = State(archi.size())

    def search(self):
        p = self.state.selectUndefinedPos()
        if p is None:
            return True
        for i in self.state.getPossibilities(p):
            self.state.set(p, i)
            if self.archi.viable(self.state, p) and self.search():
                return True
            self.state.unset(p)
        return False

class SmartEarlyChecks(EarlyChecks):
    def __init__(self, archi):
        EarlyChecks.__init__(self, archi)
        self.state = SmartState(archi.size())


def r(archi, ex):
    b = ex.search()
    print(ex.state.terrain)

a = Architects(4, [(3, 2, 1, 2), (1, 3, 2, 2), (2, 2, 3, 1), (2, 2, 1, 3)])
#r(a, EarlyChecks(a))

def solve_puzzle (clues):
    size = int(len(clues)/4)
    a = Architects(size, [clues[0:size], list(reversed(list(clues[size*2:size*3]))), list(reversed(list(clues[size*3:size*4]))), clues[size:size*2]])
    return r(a, EarlyChecks(a))

#solve_puzzle((2, 2, 1, 3, 2, 2, 3, 1, 1, 2, 2, 3, 3, 2, 1, 3))
#solve_puzzle(( 0, 0, 1, 2, 0, 2, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0 ))
solve_puzzle((3, 2, 2, 3, 2, 1, 1, 2, 3, 3, 2, 2, 5, 1, 2, 2, 4, 3, 3, 2, 1, 2, 2, 4))