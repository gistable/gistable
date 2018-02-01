#only dependency is pillow, just run "pip install pillow"
#tested on python 3.6 and 2.7
from PIL import Image

mode = ["Normal", "Twitter"][1] #0 = Normal, 1 = Twitter (add clear pixel)
number = "0001" #change to screenshot number
drive = "E:" #change to SD card drive
path = drive + "/luma/screenshots/"

if mode == "Normal": #400x240 + 320x240, black background
    screen = Image.new("RGB", (400, 480), 0x000000)
else: #RGBA for transp. pixel + 0xFF for non-transp. bg
    screen = Image.new("RGBA", (400, 480), 0xFF000000)

top = Image.open(path + "top_" + number + ".bmp")
screen.paste(top, (0, 0)) #very top left
bot = Image.open(path + "bot_" + number + ".bmp")
screen.paste(bot, (40, 240)) #Center below the top screen

if mode == "Twitter": #transparent pixel so Twitter doesn't compress
    screen.load()[0, 479] = (0, 0, 0, 0) #bottom left pixel

screen.save("screen_" + number + ".png") #save in script directory
