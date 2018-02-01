# Slightly modified from
#   https://twitter.com/petrvanblokland/status/860610270410018817
# by Petr van Blokland @petrvanblokland

def drawSierpinskiSquare(px, py, w, maxW, maxH):
    if w < 1:
        return
    for x in range(3):
        for y in range(3):
            if x == 1 and y == 1:
                fill(max(0, 0.75 - w/100))
                rect(px+w, py+w, w, w)
            elif px < maxW and py < maxH:
                drawSierpinskiSquare(px+x*w, py+y*w, w/3, maxW, maxH)

canvasSize = 500
numFrames = 40
scaleFactor = 3 ** (1/numFrames)

for frame in range(numFrames):
    newPage(canvasSize, canvasSize)
    frameDuration(1/30)  # 30 frames per second
    fill(1)  # draw a white background
    rect(0, 0, canvasSize, canvasSize)
    w = canvasSize * (scaleFactor ** frame)
    drawSierpinskiSquare(0, 0, w, canvasSize, canvasSize)

saveImage("SierpinskiSquare.gif")
