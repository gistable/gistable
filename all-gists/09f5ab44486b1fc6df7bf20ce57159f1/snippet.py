#Created by Donald K. Brown III
#Copyright 2017
#To be used with Pillow library in Python 3.5+
#Based on the 'Year in Pixels' project at http://bulletjournaling101.tumblr.com/post/149151517798/a-year-in-pixels

import datetime
from PIL import Image, ImageDraw

c = datetime.datetime.now()
yy = c.year

try:
    img = Image.open('yearincolor{}.png'.format(yy))
except FileNotFoundError:
    img = Image.new('RGB',(400,400,))

mm = c.month
dd = c.day
j1 = datetime.date(yy, 1, 1)
td = datetime.date(yy, mm, dd)
p = (td-j1).days
daystable = []
for i in range(0,20):
    a = i*20
    b = a+20
    daystable.append(list(range(a,b)))
for i in range(0,20):
    if p in daystable[i]:
        row = i
        break
startx = 20*daystable[row].index(p)
endx = startx+19
starty = 20*row
endy = starty+19

while True:
    while True:
        try:
            happy = int(input("What percent of your day was good? "))
            if not 0 <= happy <= 100:
                print("Please input an integer between 0 and 100.")
                continue
            else:
                break
        except ValueError:
            print("Please input an integer between 0 and 100.")
            continue
    while True:
        try:
            sad = int(input("What percent of your day was bad? "))
            if not 0 <= sad <= 100:
                print("Please input an integer between 0 and 100")
                continue
            else:
                break
        except ValueError:
            print("Please input an integer between 0 and 100.")
            continue
    while True:
        try:
            blargh = int(input("What percent of your day was neither good nor bad? "))
            if not 0 <= blargh <= 100:
                print("Please input an integer between 0 and 100.")
                continue
            else:
                break
        except ValueError:
            print("Please input an integer between 0 and 100.")
            continue
    if not happy+sad+blargh == 100:
        print("Your numbers don't quite add up to 100%. Let's try this again.")
        continue
    else:
        break

red = int(255*(blargh/100))
blue = int(255*(sad/100))
green = int(255*(happy/100))

draw=ImageDraw.Draw(img)
draw.rectangle([startx,starty,endx,endy],fill=(red,green,blue))
img.save("yearincolor{}.png".format(yy))

print("Success! We've updated your image! Come back tomorrow for more!")
exit(0)