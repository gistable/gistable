# for chubbyemu video at https://www.youtube.com/watch?v=omMVAtGGr_0
# THIS SCRIPT USES THE LIBRARY AT:
# https://github.com/hzeller/rpi-rgb-led-matrix
# BE SURE TO CLONE IT AND READ THE README, as highlighted in the video :)


import os, time, threading, random
import feedparser
from PIL import Image, ImageFont, ImageDraw
from random import shuffle

BITLY_ACCESS_TOKEN="BITLY_ACCESS_TOKEN"
items=[]
displayItems=[]
feeds=[
    #enter all news feeds you want here
    "http://www.fda.gov/AboutFDA/ContactFDA/StayInformed/RSSFeeds/PressReleases/rss.xml",
    "http://www.fiercepharma.com/feed",
    "http://www.fiercebiotech.com/feed",
    ]

def colorRed():
    return (255, 0, 0)

def colorGreen():
    return (0, 255, 0)

def colorBlue():
    return (0, 0, 255)

def colorRandom():
    return (random.randint(0,255), random.randint(0,255), random.randint(0,255))

def populateItems():
    #first clear out everything
    del items[:]
    del displayItems[:]

    #delete all the image files
    os.system("find . -name \*.ppm -delete")
    for url in feeds:
        feed=feedparser.parse(url)
        posts=feed["items"]
        for post in posts:
            items.append(post)
    shuffle(items)

def createLinks():
    try:
        populateItems()
        for idx, item in enumerate(items):
            writeImage(unicode(item["title"]), idx)
    except ValueError:
        print("Bummer :( I couldn't make you 'dem links :(")
    finally:
        print("\nWill get more news next half hour!\n\n")

def writeImage(url, count):
    bitIndex=0
    link, headLine="", url[:]
    def randCol(index = -1):
        if index % 3 == 0:
            return colorRed()
        elif index % 3 == 1:
            return colorGreen()
        elif index % 3 == 2:
            return colorBlue()
        else:
            return colorRandom()
    text = ((headLine, randCol(count)), (link, colorRandom()))
    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 16)
    all_text = ""
    for text_color_pair in text:
        t = text_color_pair[0]
        all_text = all_text + t
    width, ignore = font.getsize(all_text)
    im = Image.new("RGB", (width + 30, 16), "black")
    draw = ImageDraw.Draw(im)
    x = 0;
    for text_color_pair in text:
        t = text_color_pair[0]
        c = text_color_pair[1]
        draw.text((x, 0), t, c, font=font)
        x = x + font.getsize(t)[0]
    filename=str(count)+".ppm"
    displayItems.append(filename)
    im.save(filename)

def run():
    print("News Fetched at {}\n".format(time.ctime()))
    createLinks()
    threading.Timer(len(items) * 60, run).start()
    showOnLEDDisplay()

def showOnLEDDisplay():
    for disp in displayItems[:60]:
        os.system("sudo ./led-matrix -r 16 -c 3 -t 60 -m 25 -D 1 "+disp)

if __name__ == '__main__':
    run()