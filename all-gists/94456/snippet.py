from PIL import Image, ImageColor, ImageDraw
import itertools

im = Image.open("real.jpg")
pix = im.load()
draw = ImageDraw.Draw(im)

def colorTargetMatch(c):
  if c[0] < 235 and c[0] > 192: #red
    if c[1] < 190 and c[1] > 130: #green
      if c[2] < 156 and c[2] > 120: #blue
        return True
  return False

def colorBandMatch(c):
  if c[0] < 140 and c[0] > 60: #red
    if c[1] < 150 and c[1] > 80: #green
      if c[2] < 170 and c[2] > 110: #blue
        return True
  return False
  
start = -1
xlist = []
for x in range(0, im.size[0]):
  color = pix[x, 0]
  if colorBandMatch(color) == False:
    pix[x, 0] = (255, 0, 0, 255)
    if start == -1:
      start = x
  elif start != -1:
    if x - start < 10:
      print "X Axis Center Discarded; Start: ",start," End: ",x
    else:
      print "X Axis Center Found; Start: ",start," End: ",x
      xlist.append((start+x)/2)
      pix[(start+x)/2, 0] = (0,255,0,255)
    start = -1
start = -1
ylist = []
for y in range(0, im.size[1]):
  color = pix[0, y]
  if colorBandMatch(color) == False:
    pix[0, y] = (255, 0, 0, 255)
    if start == -1:
      start = y
  elif start != -1:
    if y - start < 10:
      print "Y Axis Center Discarded; Start: ",start," End: ",y
    else:
      print "Y Axis Center Found; Start: ",start," End: ",y
      ylist.append((start+y)/2)
      pix[0,(start+y)/2] = (0,255,0,255)
    start = -1

for point in itertools.product(xlist, ylist):
  x = point[0] - 17
  y = point[1] + 22
  color = pix[x, y]
  pix[x, y] = (0, 100, 0, 255)
  if colorTargetMatch(color) == True:
    pix[x, y] = (255, 255, 0, 255)
    count = 0.0
    box = 25
    for x1 in range(x-box, x+box):
      color = pix[x1, y-box]
      if colorTargetMatch(color) == True:
        count += 1
    for x2 in range(x-box, x+box):
      color = pix[x2, y+box]
      if colorTargetMatch(color) == True:
        count += 1
    for y1 in range(y-box, y+box):
      color = pix[x-box,y1]
      if colorTargetMatch(color) == True:
        count += 1
    for y2 in range(y-box, y+box):
      color = pix[x+box,y2]
      if colorTargetMatch(color) == True:
        count += 1
    ratio = count / (box*2*4)

    #draw.rectangle(((x-box, y-box),(x+box, y+box)), outline=(255,255,0))
    
    draw.text((x, y-5), str(ratio), fill=(0,0,0))
    #draw.rectangle(((x-box, y-box),(x+box, y+box)), outline=(0,0,0))
    if ratio > 0.09 and ratio < 0.2:
      pix[x, y] = (255, 0, 255, 255)
      draw.rectangle(((x-box, y-box),(x+box, y+box)), outline=(0,0,0))
      print ratio
      print point
    #yay, the point is actually on the blah
  

im.show()
im.save("ScanOut", "PNG")