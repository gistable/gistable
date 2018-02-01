import sys, pygame, os, StringIO
from epubzilla.epubzilla import Epub
import random

ebooks = []

for file in os.listdir("./"):
    if file.endswith(".epub"):
        ebooks.append(Epub.from_file(file))


pygame.init()
if len(sys.argv) == 3:
	size = width, height = int(float(sys.argv[1])), int(float(sys.argv[2]))
else:
    size = width, height = 1920, 1080

fontSize = height / 55
myFont = pygame.font.SysFont("monospace", fontSize)
speed = width / 960
scale = int(height / 4)
bookHeight = int(round(1.314 * scale, -1))
bookWidth = 1 * scale

noCoverCover = pygame.transform.scale(pygame.image.load("noCoverCover.jpg"), (bookWidth, bookHeight))

black = 0, 0, 0

screen = pygame.display.set_mode(size)
pygame.display.toggle_fullscreen()

eCovers = []


spacing = 0

random.shuffle(ebooks);

for book in ebooks:
    output = open("tmp.jpg", 'wb')
    #print(book.title)
    try:
        #print(book.cover.tag['href'])
        output.write(book.cover.get_file())
        output.close()
        eCovers.append((pygame.transform.scale(pygame.image.load("tmp.jpg"), (bookWidth, bookHeight)), spacing * (bookWidth + 30)))
    
    except:
        #print("No cover on " + book.title + " giving temp cover")
        eCovers.append((noCoverCover, spacing * (bookWidth + 30)))
        output.close()
    spacing = spacing + 1

x_offset = 0


background = pygame.image.load("bookshelf2.jpg")
backRec = pygame.Rect(0, 0, width, height)

background = pygame.transform.scale(background, (width, height))

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    screen.fill(black)
    

    #look for keypress to close fullscreen
    if(pygame.key.get_pressed()[pygame.K_ESCAPE]):
        pygame.display.toggle_fullscreen()
        
    screen.blit(background, backRec)
    index = 0
    for cover in eCovers: 
        eCovers[index] = (cover[0], cover[1] - speed)
        if(cover[1] <= width + bookWidth + 15):
            screen.blit(cover[0], pygame.Rect(cover[1], height / 2 - bookHeight / 2, 20, 20))        
            if cover[1] < -bookWidth - 20:
                #print("changed position of " + ebooks[index].title + " its position is: " + str(cover[1]))
                eCovers[index] = (cover[0], (len(eCovers) - 1) * (bookWidth + 30))

            if cover[0] == noCoverCover:
                
                fontDecrease = 1
                while myFont.render(ebooks[index].title, 1, black).get_width() >= bookWidth or myFont.render(ebooks[index].author, 1, black).get_width() >= bookWidth:
                    
                    myFont = pygame.font.SysFont("monospace", fontSize - fontDecrease)
                    fontDecrease += 1
                
                title = myFont.render(ebooks[index].title, 1, black)
                author = myFont.render(ebooks[index].author, 1, black)
                screen.blit(title, (cover[1] + bookWidth / 2 - title.get_width() / 2, height / 2 - bookHeight / 2 + bookHeight / 4))
                screen.blit(author, (cover[1] + bookWidth / 2 - author.get_width() / 2, height / 2 - bookHeight / 2 + bookHeight / 4 + author.get_height() + 2))
                myFont = pygame.font.SysFont("monospace", fontSize)
        index = index + 1
    pygame.display.flip()