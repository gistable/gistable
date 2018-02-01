import pygame
from pygame.locals import *
import re
import time
from collections import namedtuple

def main():
	haveUserInput = False	
	name = ""
	buffer = []
	dt = time.time()

	names = open('names.csv', 'a')
	names.write("\nID,FIRST,LAST,POS\n")

	pygame.init()

	infoObject = pygame.display.Info()
	screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)

	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill((0, 0, 0))

	while True:
		if (time.time() - dt) > 5 and haveUserInput:
			haveUserInput = False
			name = ""
			dt = time.time()
			background.fill((0, 0, 0))
			redrawBackground(background, screen)

		for event in pygame.event.get():
			if event.type == QUIT:
				names.close()
				return

			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					names.close()
					return
				elif event.key == K_RETURN:
					print "enter pressed"
					# buffer.append("\n")
					User = readCard(buffer)
					if User:
						haveUserInput = True
						name = User.fname + " " + User.lname
						names.write(str(User.id) + "," + User.fname + "," + User.lname + "," + User.pos + "\n")
						background.fill((255, 255, 255))
						redrawBackground(background, screen)
					else:
						haveUserInput = False
					buffer = []
				else:
					print "this ran"
					buffer.append(event.unicode)
					haveUserInput = False

		screen.blit(background, (0, 0))
		redrawBackground(background, screen)
		drawWords(background, screen, name, haveUserInput)
		pygame.display.flip()

def drawWords(background, screen, data, flag):
	pygame.font.init()
	font = pygame.font.Font("SamsungImaginationBold.otf", 60)
	# word = "dank memes"
	word = "Please swipe your ID."
	if (flag):
		word = "Thank you, " + data

	text = font.render(word, True, (255, 0, 0))
	textpos = text.get_rect()
	textpos.centerx = background.get_rect().centerx
	textpos.centery = background.get_rect().centery
	background.blit(text, textpos)
	screen.blit(background, (0, 0))
	pygame.display.flip()

def redrawBackground(background, screen):
	# background.fill((0, 0, 0))
	screen.blit(background, (0, 0))

# swipe logic - find required string w/relevant data
def readCard(buffer):
	isCorrect = False
	# while True:
	swipe = "".join(buffer)
	matchPercent = re.match(r'^%', swipe)
	matchEqual = False

	if ("=" in swipe):
		matchEqual = True
	if (matchPercent and matchEqual):
		isCorrect = True
		# print "MATCH"
		temp = parseString(swipe)
	# else:
		# print "NO MATCH"
	if (isCorrect == True):
		return temp
	return False

# swipe logic - parse string for pieces of data
def parseString(swipe):
	userid = 0
	lname = ""
	fname = ""
	pos = ""

	swipe = swipe.replace("%", "")
	swipe = swipe.replace("?", "")
	# print ("DATA: " + swipe)

	list = swipe.split("=")
	userid = list[0]
	lname = list[1]
	fname = list[2]
	pos = list[3]
	# print ("ID: " + userid + "   LNAME: " + lname + "   FNAME: " + fname + "   POS: " + pos)

	User = namedtuple('User', ['fname', 'lname', 'id', 'pos'], verbose=False)
	User.fname = fname.title()
	User.lname = lname.title()
	User.id = userid
	User.pos = pos
	return User

main()