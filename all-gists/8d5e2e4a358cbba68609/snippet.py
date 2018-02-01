import random

# A4 paper size in mm
paperWidth = 210 
paperHeight = 297

# bleed for printing
bleed = 20

# book spine
spineWidth = 14

# artwork dimensions
artworkWidth = bleed * 2 + paperWidth * 2 + spineWidth
artworkHeight = bleed * 2 + paperHeight

# convert units from points to millimeters
# 1 point = 0.3527mm
pointsToMillimeters = 1 / 0.3527
size(artworkWidth * pointsToMillimeters, artworkHeight * pointsToMillimeters)
scale(pointsToMillimeters)

# starting coordinates
x0 = bleed
y0 = bleed

# grid rows and columns
numRows = 5
numCols = 14

# cell dimensions
cellSize = 27
cellMargin = 3
    
# a number that affects how much randomness is applied to each row
randomFactor = 0

# a number that affects randomFactor's rate of increase
multiplier = 0.9

# disable strokes
stroke(None)

# draw the grid
for cellRow in range(0, numRows):
    for cellCol in range(0, numCols):
        
        # x and y coordinates for each cell
        cellX = x0 + cellCol * (cellSize + cellMargin)
        cellY = y0 + cellRow * (cellSize + cellMargin)
        
        # leave space for the book spine
        if cellCol >= 7: cellX += spineWidth
        
        # each cell is divided into a number of squares
        numSquares = random.randint(2, 6)
        
        # randomize square size and make it fit
        # the space available in the cell
        maxSquareSize = cellSize / numSquares
        squareSize = random.randint(2, 15 - numSquares)
        if squareSize > maxSquareSize: squareSize = maxSquareSize
        
        # space between squares
        space = (cellSize - squareSize * numSquares) / (numSquares - 1)
        
        # draw the squares in each cell
        for squareRow in range(0, numSquares):
            for squareCol in range(0, numSquares):
                
                # randomize color
                c1 = random.uniform(0.1, 0.5)
                c2 = random.uniform(0.2, 0.9)
                cmykFill(c1, c2, c2, 0)

                # generate 3 random numbers that will be
                # used for rotation, scale, and size
                r1 = random.uniform(-1, 1) * randomFactor
                r2 = random.uniform(-1, 1) * randomFactor
                r3 = random.uniform(1, 3) * randomFactor
                
                # draw the square
                save()
                translate(cellX + squareSize * squareCol + space * squareCol, cellY + squareSize * squareRow + space * squareRow)
                rotate(r1 * 10)
                scale(1 + r1, 1 + r2)
                rect(0, 0, squareSize + r3, squareSize + r3)
                restore()

    # randomFactor is increased for each row
    # every row is more random than the previous row
    randomFactor += random.random() * multiplier
