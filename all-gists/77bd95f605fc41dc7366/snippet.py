#!/usr/bin/env python

#Some mazes classes translated from Ruby 
#from book "Mazes for Programmers" by Jamis Buck.
#https://pragprog.com/book/jbmaze/mazes-for-programmers
#
#Includes modifications.
#
#Execute this and you see mazes.

import random

class Cell:
    
    def __init__(self,row,column):
        self.row=row
        self.column=column
        self.north=None
        self.east=None
        self.south=None
        self.west=None
        self.links=dict()

    def link(self,cell,bidi=True):
        self.links[cell] = True
        if bidi==True:
            cell.link(self,False)
        return self

    def unlink(self,cell,bidi=True):
        try:
            del self.links[cell]
        except KeyError:
            pass
        if bidi==True:
            cell.unlink(self, false)
        return self

    def getLinks(self):
        return self.links.keys()
    
    def linked(self,cell):
        return self.links.has_key(cell)

    def neighbors(self):
        neighborsList = []
        if self.north:
            neighborsList.append(self.north)
        if self.east:
            neighborsList.append(self.east)
        if self.south:
            neighborsList.append(self.south)
        if self.west:
            neighborsList.append(self.west)
        return neighborsList

    def hasNeighbor(self,direction):
        if direction=="north" and self.linked(self.north):
            return True
        if direction=="east" and self.linked(self.east):
            return True
        if direction=="south" and self.linked(self.south):
            return True
        if direction=="west" and self.linked(self.west):
            return True

        return False

    #return Distances from this cell to all other cells
    def getDistances(self):
        distances=Distances(self)
        frontier=[]
        frontier.append(self)
        while len(frontier)>0:
            newFrontier=[]
            for cell in frontier:
                for linked in cell.getLinks():
                    if distances.getDistanceTo(linked) is None:
                        dist=distances.getDistanceTo(cell)
                        distances.setDistanceTo(linked,dist+1)
                        newFrontier.append(linked)
            frontier=newFrontier
        return distances

    def __str__(self):
        output="Cell[%d,%d], Linked neighbors: " % (self.row,self.column)
        if self.linked(self.north):
            output=output+" North: YES "
        else:
            output=output+" North: NO "

        if self.linked(self.east):
            output=output+" East: YES "
        else:
            output=output+" East: NO "
        if self.linked(self.south):
            output=output+" South: YES "
        else:
            output=output+" South: NO "
        if self.linked(self.west):
            output=output+" West: YES "
        else:
            output=output+" West: NO "

        return output

class Distances:

    def __init__(self,rootCell):
        self.rootCell=rootCell
        self.cells=dict()
        self.cells[self.rootCell]=0

    def getDistanceTo(self,cell):
        return self.cells.get(cell,None)

    def setDistanceTo(self,cell,distance):
        self.cells[cell]=distance

    def getCells(self):
        return self.cells.keys()

    def isPartOfPath(self,cell):
        return self.cells.has_key(cell)

    def __len__(self):
        return len(self.cells.keys())

    def pathTo(self,goal):
        current=goal
        breadcrumbs = Distances(self.rootCell)
        breadcrumbs.setDistanceTo(current,self.cells[current])

        while current is not self.rootCell:
            for neighbor in current.getLinks():
                if self.cells[neighbor] < self.cells[current]:
                    breadcrumbs.setDistanceTo(neighbor,self.cells[neighbor])
                    current=neighbor
                    break
        return breadcrumbs


class Grid:

    def __init__(self,rows,columns,cellClass=Cell):
        self.CellClass=cellClass
        self.rows=rows
        self.columns=columns
        self.grid=self.prepareGrid()
        self.distances=None
        self.configureCells()

    def prepareGrid(self):
        rowList=[]
        i=0
        j=0
        for i in range(self.rows):
            columnList=[]
            for j in range(self.columns):
                columnList.append(self.CellClass(i,j))
            rowList.append(columnList)
        return rowList

    def eachRow(self):
        for row in self.grid:
            yield row

    def eachCell(self):
        for row in self.grid:
            for cell in row:
                yield cell      

    def configureCells(self):
        for cell in self.eachCell():
            row=cell.row
            col=cell.column
            cell.north=self.getNeighbor(row-1,col)
            cell.east=self.getNeighbor(row,col+1)
            cell.south=self.getNeighbor(row+1,col)
            cell.west=self.getNeighbor(row,col-1)

    def getCell(self,row,column):
        return self.grid[row][column]

    def getNeighbor(self,row,column):
        if not (0 <= row < self.rows):
            return None
        if not (0 <= column < self.columns):
            return None
        return self.grid[row][column]

    def size(self):
        return self.rows*self.columns

    def randomCell(self):
        row=random.randint(0, self.rows-1)
        column=self.grid
        column = random.randint(0,len(self.grid[row])-1)
        return self.grid[row][column]

    def contentsOf(self,cell):
        return "   "

    def __str__(self):
        return self.asciiStr()

    def unicodeStr(self):
        pass

    def asciiStr(self):
        output = "+" + "---+" * self.columns + "\n"
        for row in self.eachRow():
            top = "|"
            bottom = "+"
            for cell in row:
                if not cell:                
                    cell=Cell(-1,-1)
                body = "%s" % self.contentsOf(cell)
                if cell.linked(cell.east):
                    east_boundary=" "
                else:
                    east_boundary="|"

                top = top+ body + east_boundary
                if cell.linked(cell.south):
                    south_boundary="   "
                else:
                    south_boundary="---"
                corner = "+"
                bottom =bottom+ south_boundary+ corner
            
            output=output+top+"\n"
            output=output+bottom+"\n"
        return output
 
class DistanceGrid(Grid):

    #def __init__(self,rows,columns,cellClass=Cell):
    #    super(Grid, self).__init__(rows,columns,cellClass)

    def contentsOf(self,cell):

        if  self.distances.getDistanceTo(cell) is not None and self.distances.getDistanceTo(cell) is not None:
            n=self.distances.getDistanceTo(cell)
            return "%03d" % n
        else:
            return "   " #super(Grid, self).contentsOf(cell)



def initBinaryTreeMaze(grid):
    for cell in grid.eachCell():
        neighbors=[]
        if cell.north:
            neighbors.append(cell.north)
        if cell.east:
            neighbors.append(cell.east)
        if len(neighbors)>0:
            if len(neighbors)==1:
                ind=0
            else:
                ind=random.randint(0,len(neighbors)-1)
            neighbor=neighbors[ind]
            if neighbor:
                cell.link(neighbor)
    return grid


def initRecursiveBacktrackerMaze(grid):
    stack = [] 
    stack.append(grid.randomCell())

    while len(stack)>0: 
        current = stack[-1]
        neighbors=[]
        for n in current.neighbors():
            if len(n.getLinks())==0:
                neighbors.append(n)

        if len(neighbors)==0:
            stack.pop()
        else:
            neighbor = random.choice(neighbors)
            current.link(neighbor) 
            stack.append(neighbor) 

    return grid


def initSidewinderMaze(grid):
    tf=[True,False]
    for row in grid.eachRow():
        run=[]
        for cell in row:
            run.append(cell)
            at_eastern_boundary = (cell.east == None)
            at_northern_boundary = (cell.north == None)
            #note: ruby: 0 == True
            should_close_out =at_eastern_boundary or ( at_northern_boundary==False and random.choice(tf) == True)
            if should_close_out == True:
                member = random.choice(run)
                if member.north:
                    member.link(member.north)
                run=[]
            else:
                cell.link(cell.east)
    return grid

#====================
def initRecursiveBacktrackerMaze2(grid):
    rbWalkFrom(grid.randomCell())
    return grid

def rbWalkFrom(cell):
    shuffledNeighbors=random.sample(cell.neighbors(),len(cell.neighbors()))
    for neighbor in shuffledNeighbors:
        if len(neighbor.getLinks())==0:
            cell.link(neighbor)
            rbWalkFrom(neighbor)

if __name__ == "__main__": 
    rows,columns=10,10
    grid=Grid(rows,columns)
    grid=initBinaryTreeMaze(grid)
    print("Binary Tree Maze:")
    print(grid)
    grid=DistanceGrid(rows,columns)
    grid=initRecursiveBacktrackerMaze(grid)

    startRow=0#random.randint(0, rows-1)
    startColumn=0#random.randint(0, columns-1)
    start = grid.getCell(startRow,startColumn)
    goalRow=rows-1#random.randint(0, rows-1)
    goalColumn=columns-1#random.randint(0, columns-1)

    goal= grid.getCell(goalRow,goalColumn)
    distances = start.getDistances()
    grid.distances = distances.pathTo(goal)
    print("Recursive Backtracker Maze:")
    print("Start: ", start)
    print("Goal: ", goal)
    print(grid)

    grid=Grid(rows,columns)
    grid=initSidewinderMaze(grid)
    print("Sidewinder Maze:")
    print(grid)
