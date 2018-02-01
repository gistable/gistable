import autopy.mouse as mouse
from PIL import ImageGrab
from autopy.mouse import LEFT_BUTTON, RIGHT_BUTTON
import time

tiles = ["224224224255","255255153255", "2553636255", "0242174255", "44139255255", "221165250255", "552340255", "255211189255", "1590242255", "2551810255", "192192192255", "2062500255"]
tileMapping = "0123456789ABCDEFGHIJKLMOPQRSTUWXYZ"

width = 570
height = 682

x = 54
y = 142

tileWidth = 80
tileHeight = 84

boardX = 7
boardY = 8

def getSum(value):
	suma = ""
	for i in value:
		suma = suma + str(i)
	return suma

def getBoard():
	board = []
	screenshot = ImageGrab.grab()

	for j in range(boardY):	
		current = ""
		for i in range(boardX):
			currentValue = screenshot.getpixel((x+tileWidth*i + tileWidth/4, y+tileHeight*j + tileHeight/4))

			index = 33

			try:
				index = tiles.index(getSum(currentValue))
			except:
				print("Unidentified block")

			current = current + tileMapping[index]

		board.append(current)
	return(board)


visited = []
for i in range(boardY):
	v = []
	for j in range(boardX):
		v.append(False)
	visited.append(v)

def dfs(start, currentX, currentY, root):
	if(currentX < 0 or currentX >= boardX or currentY < 0 or currentY >= boardY):
		return '0';

	if(visited[currentY][currentX]):
		return '0';
	visited[currentY][currentX] = True;

 	if(board[currentY][currentX] == start and not root):
		return "";

	if(board[currentY][currentX] != '0' and not root):
		return '0'


	left = dfs(start, currentX-1, currentY, False);
	right = dfs(start, currentX+1, currentY, False);
	up = dfs(start, currentX, currentY-1, False);
	down = dfs(start, currentX, currentY+1, False);

	if(left != '0'):
		return 'l'+left;
	if(right != '0'):
		return 'r'+right;
	if(up != '0'):
		return 'u'+up;
	if(down != '0'):
		return 'd'+down;

	return '0';


def executeMove(startX, startY, moveSequence):
	print(moveSequence)

	sx = x + startX * tileWidth + tileWidth/4
	sy = y + startY * tileHeight + tileHeight/4

	mouse.move(sx, sy)
	mouse.click()
	mouse.toggle(True)

	for i in range(len(moveSequence)):
		if(moveSequence[i] == 'l'):
			sx = sx - tileWidth
		if(moveSequence[i] == 'r'):
			sx = sx + tileWidth
		if(moveSequence[i] == 'u'):
			sy = sy - tileHeight
		if(moveSequence[i] == 'd'):
			sy = sy + tileHeight
		mouse.smooth_move(sx, sy)
	mouse.toggle(False)

def getBestMove(board):

	minLength = 10000
	bestMove = ""
	bestX = 0
	bestY = 0

	for i in range(boardY):
		for j in range(boardX):
			if(board[i][j] != '0'):

				for k in range(boardY):
					for l in range(boardX):
						visited[k][l] = False;

				guess = dfs(board[i][j], j, i, True);
				if(guess != '0'):
					if(len(guess) < minLength):
						bestMove = guess
						minLength = len(guess)
						bestX = j
						bestY = i

	if(bestMove != ""):
		print("Move found, executing")
		executeMove(bestX, bestY, bestMove)
		print("Finished executing move")
	else:
		print("No move found")

while(True):

	print("Getting board...")
	board = getBoard();
	print("Got board, finding a possible move")
	getBestMove(board)


	
					



