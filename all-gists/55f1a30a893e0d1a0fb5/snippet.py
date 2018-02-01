# Physics stolen from:
# http://giphy.com/gifs/wave-circle-point-13ePqdDflwat9e

def blobPos(pt, r, a):
    x, y = pt
    x += cos(a) * r
    y += sin(a) * r
    return (x, y)

def drawGrid(cells):
    fill(None)
    stroke(0)
    strokeWidth(18)
    for i in range(len(cells)-1):
        for j in range(len(cells[i])-1):
            pt1 = cells[i][j+1]
            pt2 = cells[i+1][j]
            line(pt1, pt2)
    
NCELLS = 18
CELLSIZE = 45
RADIUS = 70
OFFSET = (1000 - (NCELLS - 1) * CELLSIZE) / 2
NFRAMES = 10  #50

for frame in range(NFRAMES):
    newPage(500, 500)
    frameDuration(1/25)
    fill(1)
    rect(0, 0, 500, 500)  # background
    scale(0.5)
    translate(OFFSET, OFFSET)
    cells = [[None] * NCELLS for i in range(NCELLS)]
    phase = 2 * pi * frame / NFRAMES
    for i in range(NCELLS):
        for j in range(NCELLS):
            angle = (i - j) * 0.1
            pt = blobPos((i * CELLSIZE, j * CELLSIZE), RADIUS, angle + phase)
            cells[j][i] = pt
    drawGrid(cells)

# saveImage("circlewavegrid.gif")
