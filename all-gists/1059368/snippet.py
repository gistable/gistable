    def near(self,x1,y1,x2,y2):
        """Checks if x1,y1 near x2,y2"""
        if x1 - x2 >= -1 and x1 - x2 <= 1 and\
                 y1 - y2 >= -1 and y1 - y2 <= 1:
            return True
        else:
            return False

    def hasSpaceAround(self,x,y):
        """Checks if there is free cells
            around x,y"""
        global gamemap
        c = 0
        for x2 in xrange(-2,2):
            for y2 in xrange(-2,2):
                if self.near(x, y,x + x2,y + y2):
                    if not gamemap[x + x2][y + y2].type[0]:
                        c += 1
        if c >= 8:
            return False
        else:
            return True
