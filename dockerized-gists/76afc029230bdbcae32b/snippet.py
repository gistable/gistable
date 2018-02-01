DEBUG = True

max_frames = 80.
grid = 100
offset = 25
cent_width = 25

def setup():
    size(400, 400)
    if DEBUG:
        frameRate(100/3)
    rectMode(CENTER)
    fill(0xff)
    noStroke()

def draw():
    t = frameCount / max_frames
    background(0)
    
    translate(width/2, height/2)
    
    for i in range(4):
        rotate(HALF_PI)
        draw_center(t)
        draw_center(t, shifted=True)
        draw_upshot(t)

    if not DEBUG:
        filter(BLUR, .8)
        saveFrame('f###.gif')
        if frameCount == max_frames:
            exit()

def draw_center(t, shifted=False):
    for x in range(-int(width/2./grid)-1, int(width/2./grid)+2, 1):
        for y in range(-int(height/2./grid)-1, int(height/2./grid)+2, 1):
            pushMatrix()
            translate(grid*x, grid*y)
            if shifted:
                translate(grid/2., grid/2.)
            if not shifted and not .5 <= t % 1 < .75:
                rotate(t * TWO_PI)
            elif shifted and not t % 1 < .25:
                rotate (-t * TWO_PI)
            rect(0, 0, cent_width, cent_width, 5)
            popMatrix()

def draw_upshot(t):
    for x in range(-int(width/2./grid)-1, int(width/2./grid)+2, 1):
        for y in range(-int(height/2./grid)-1, int(height/2./grid)+2, 1):
            pushMatrix()
            translate(grid*x, grid*y)
            if t % 1 <= .25:
                pushMatrix()
                rotate(t * TWO_PI)
                rect(offset, 0, 10, 2*cent_width + 10, 5)
                popMatrix()
            if .25 < t % 1 < .5:
                rect(map(t%1, .25, .5, 0, grid / 2.), -offset, 2*cent_width + 10, 10, 5)
            if .5 <= t % 1 < .75:
                pushMatrix()
                translate(grid / 2., grid / 2.)
                rotate(-2 * t * PI)
                rect(grid / 2. - offset, 0, 10, 2*cent_width + 10, 5)
                popMatrix()
            if .75 <= t % 1:
                rect(map(t%1, .25, .5, -grid / 2., 0), -offset, 2*cent_width + 10, 10, 5)
            popMatrix()
