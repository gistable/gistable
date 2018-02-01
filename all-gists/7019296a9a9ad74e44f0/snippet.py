import microbit, random

# from Python 3 source
def shuffle(x):
    for i in reversed(range(1, len(x))):
        # pick an element in x[:i+1] with which to exchange x[i]
        j = int(random.random() * (i+1))
        x[i], x[j] = x[j], x[i]

# correct viewport onto maze so the whole screen is always used
def correct(x,y):
    if x<2: x=2
    if x>size-3: x = size-3
    if y<2: y=2
    if y>size-3: y = size-3
    return x,y

# correct player position so centred unless near the edge
def player_correct(x,y):
    if x>2 and x<size-2: x=2
    if x>size-3: x = 5-(size-x)
    if y>2 and y<size-2: y=2
    if y>size-3: y = 5-(size-y)
    return x,y

# display a viewport onto the maze at position x,y    
def set_grid(x,y):
    x,y = correct(x,y)
    for iy in range(5):
         for ix in range(5):
             microbit.display.set_pixel(ix,iy,mazeBrightness*pos(x+ix-2,y+iy-2))
             
# returns -1 to 1 from -1024 to +1024, empirically calculated
def tilt_scale(a):
    a = a + 1024 # range 0 to 2048
    a = min(a, 2048)
    a = max(a, 0)
    # < 512 = 0, 512-853(512+341) = 1, 853-1194 = 2, 1194-1536 = 3,  1536-2048 = 4
    if a<512: return -1
    if a<853: return 0
    if a<1194: return 0
    if a<1536: return 0
    return 1
    
def get_tilt():
    x,y,z = microbit.accelerometer.get_values()
    #print(x+1024,y+1024,z+1024)
    x = tilt_scale(x)
    y = tilt_scale(y)
    z = tilt_scale(z)
    #print(x,y,z)
    return x,y,z


def shuffled(x):
    y = list(x)
    shuffle(y)
    return y

DIRECTIONS = (
    (0, -1),
    (0, 1),
    (1, 0),
    (-1, 0),
)

# code adjusted from https://29a.ch/2009/9/7/generating-maps-mazes-with-python
def make_maze(width, height, cellsize):
    cellsize1 = cellsize+1 # cellsize including one wall
    field_width = width*cellsize1+1
    field_height = height*cellsize1+1
    field = [0]*(field_width*field_height)
    stack = [(0, 0, shuffled(DIRECTIONS))]
    while stack:
        x, y, directions = stack[-1]
        dx, dy = directions.pop()
        # no other ways to go from here
        if not directions:
            stack.pop()
        # new cell
        nx = x+dx
        ny = y+dy
        # out of bounds
        if not (0 <= nx < width and 0 <= ny < height):
            continue
        # index of new cell in field
        fx = 1+nx*cellsize1
        fy = 1+ny*cellsize1
        fi = fx+fy*field_width
        # already visited
        if field[fi]:
            continue
        # tear down walls
        if dx > 0:
            a = -1
            b = field_width
        elif dx < 0:
            a = cellsize
            b = field_width
        elif dy > 0:
            a = -field_width
            b = 1
        else:
            a = cellsize*field_width
            b = 1
        for offset in range(cellsize):
            field[fi+a+b*offset] = 1
        # clear cell
        for y in range(0, cellsize):
            for x in range(0, cellsize):
                field[fi+x+y*field_width] = 1
        # visit cell
        stack.append([nx, ny, shuffled(DIRECTIONS)])
    for i in field:
        field[i] = 1-field[i]
    return field

#convert 2d coords to 1d array
def pos(x,y):
    return maze[y*size+x]

def set_pos(x,y,v):
    maze[y*size+x] = v

#find an empty square
def get_space():
    startPos = False
    while startPos == False:
        x = random.randint(1,size-1)
        y = random.randint(1,size-1)
        if pos(x,y) == 0:
            print("found startPos",x,y, pos(x,y))
            startPos = True
    return x,y

gameSpeed = 300
size = 6 # more than 6 runs out of memory
mazeBrightness = 1
goalBrightness = 5 # goalBrightness * mazeBrightness < 9
maze = make_maze(size,size,1)
print(maze,len(maze))
# correct size to allow for walls etc
size = 2*size+1

# create a goal square
goalX,goalY = get_space()
set_pos(goalX,goalY,goalBrightness)

# create player
x,y = get_space()

won = False
while won == False:
    set_grid(x,y) # draw viewport onto maze
    xv,yv,zv = get_tilt()
    
    dx,dy = player_correct(x,y)
    microbit.display.set_pixel(dx,dy,9) # draw player
    
    # stop moving off maze
    if x+xv < 0 or x+xv > size-1: xv = 0
    if y+yv < 0 or y+yv > size-1: yv = 0
    
    # if we found the goal, stop
    if pos(x+xv,y+yv) == goalBrightness:
        won = True
    # if moving to a blank square, allow
    if pos(x+xv,y+yv) == 0:
        x += xv
        y += yv
    microbit.sleep(gameSpeed)
microbit.display.show("Win!")