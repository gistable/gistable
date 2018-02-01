# Not much fun unless you have one of these:
#    http://www.instructables.com/id/The-4x4x4-LED-cube-Arduino/
#
import random

DEBUG = True # Visualize the movement. Hit/hold return to progress the snake

CUBESIZE = 4

ouf = open("snake.txt",'w')

# Cube is 3D array of length CUBESIZE
# Snake is represented by the integers SNAKELENGTH to 1 (from head to tail)
# Apples are represented by -1
# Blank space by 0
#
# cube[ updown ][ leftright ][ frontback ]
cube = []
for z in range(CUBESIZE):
    plane = []
    for y in range(CUBESIZE):
        plane.append( [0]*CUBESIZE )
    cube.append(plane)
leds = CUBESIZE*CUBESIZE*CUBESIZE

def iterate_cube(cube):
    for z in range(CUBESIZE):
        for y in range(CUBESIZE):
            for x in range(CUBESIZE):
                yield (z,y,x,cube[z][y][x])

def add_apple(cube, snakelen):
    # There should be CUBESIZE**3 - snakelen empty spaces.
    ax = random.choice(range(leds - snakelen))
    ix = 0
    for z,y,x,v in iterate_cube(cube):
        if v == 0:
            if ix == ax:
                cube[z][y][x] = -1
                return (z,y,x)
            ix += 1

    raise Exception("Should not get here. ax=%s ix=%s" % (ax,ix))

def find_available_moves(cube, snake_head):
    # Reads the cube, and returns a list of all possible new head positions (z,y,x) for the snake.
    moves = []
    z,y,x = snake_head
    if z > 0 and cube[z-1][y][x] in [0,-1]:
        # Can move down
        moves.append( (z-1,y,x) )

    if z < (CUBESIZE-1) and cube[z+1][y][x] in [0,-1]:
        # Can move up
        moves.append( (z+1,y,x) )

    if y > 0 and cube[z][y-1][x] in [0,-1]:
        # Can move left
        moves.append( (z,y-1,x) )

    if y < (CUBESIZE-1) and cube[z][y+1][x] in [0,-1]:
        # Can move right
        moves.append( (z,y+1,x) )

    if x > 0 and cube[z][y][x-1] in [0,-1]:
        # Can move back
        moves.append( (z,y,x-1) )

    if x < (CUBESIZE-1) and cube[z][y][x+1] in [0,-1]:
        # Can move forward
        moves.append( (z,y,x+1) )
        
    return moves

def output_cube(cube, snake_head, snakelen):

    bools = []
    for z,y,x,v in iterate_cube(cube):
        if v != 0:
            bools.append(1)
        else:
            bools.append(0)
    frame = ""
    ix = 0
    for zx in range(CUBESIZE):
        for yx in range(CUBESIZE):
            frame += 'B'
            frame += "".join([str(b) for b in bools[ix*CUBESIZE:(ix+1)*CUBESIZE]])
            frame += ","
            ix += 1
        frame += " "
    frame += "10,"
    ouf.write(frame + "\n")

    if DEBUG:
        print frame
        print "snake_head at\tz=%s\ty=%s\tx=%s" % snake_head
        print "snake length: %s" % snakelen

        layers = []
        for ii in range(CUBESIZE*2 - 1):
            layers.append( [" "]*(CUBESIZE+2)*CUBESIZE )

        for z,y,x,v in iterate_cube(cube):
            fmtv = "."
            if v == -1:
                fmtv = "@"
            if v == snakelen:
                fmtv = '%'
            elif v > 0:
                fmtv = '#'
            layers[ z+x ][ 1 + (z*(CUBESIZE+2)) + y ] = fmtv

        for line in layers:
            print "".join(line)
        
        raw_input()



# Initiailize the cube, and snake
cube[0][0][0] = 1
snake_head = (0,0,0)
snakelen = 1
cube[2][2][2] = -1
apple_coords = (2,2,2)

output_cube(cube, snake_head, snakelen)

available_moves = find_available_moves(cube, snake_head)
while available_moves:
    # Find available moves (next head positions)

    def is_good_move(move, snake_head, apple_coords):
        # does the move get us towarsd the apple.
        mz,my,mx = move
        az,ay,ax = apple_coords
        sz,sy,sx = snake_head
        cur_dist = abs(sz-az) + abs(sy-ay) + abs(sx-ax)
        move_dist = abs(mz-az) + abs(my-ay) + abs(mx-ax)
        return (move_dist < cur_dist)
       
    good_moves = [move for move in available_moves if is_good_move(move, snake_head, apple_coords)]
    if good_moves:
        # Randomly select any move that moves snake head towards apple
        selected_move = random.choice(good_moves)
    else:
        # Select any move.
        selected_move = random.choice(available_moves)

    mz,my,mx = selected_move
    if cube[mz][my][mx] == -1:
        # move means apple is eaten:
        snakelen += 1
        cube[mz][my][mx] = snakelen
        snake_head = (mz,my,mx)
        apple_coords = add_apple(cube, snakelen)
    else:
        # Move snake along by subtracing 1 from all bits of snake body
        for z,y,x,v  in iterate_cube(cube):
            if v > 0:
                cube[z][y][x] -= 1
        snake_head = (mz,my,mx)
        cube[mz][my][mx] = snakelen

    output_cube(cube, snake_head, snakelen)
    available_moves = find_available_moves(cube, snake_head)

print "Snake got to %s long" % snakelen
ouf.close()