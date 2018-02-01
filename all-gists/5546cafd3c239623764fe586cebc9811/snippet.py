# http://dailydrawbot.tumblr.com/post/143801148619/square-vs-lozenge

def rotatedSquare(x, y, squareSize, angle):
    offsetSin = squareSize * sin(radians(angle))
    save()
    translate(x + offsetSin, 0)
    rotate(angle)
    rect(0, 0, squareSize, squareSize)
    restore()

canvasSize = 500
nFrames = 100

squareSize = 56
nSquares = 6  # must be even

for frame in range(nFrames):
    newPage(canvasSize, canvasSize)
    frameDuration(1/20)
    fill(0)
    rect(0, 0, canvasSize, canvasSize)
    fill(1)
    stroke(1)
    strokeWidth(0.1)
    translate(canvasSize/2, canvasSize/2)

    angle = (90 * frame / nFrames)
    offset = squareSize * (sin(radians(angle)) + cos(radians(angle)))
    translate(-(nSquares//2) * offset, -(nSquares//2) * offset)

    for j in range(nSquares):
        save()
        for i in range(nSquares):
            rotatedSquare(0, 0, squareSize, angle)
            translate(offset, 0)
            angle = 90 - angle
        restore()
        translate(0, offset)
        angle = 90 - angle

saveImage("SquareVsLozenge.gif")
