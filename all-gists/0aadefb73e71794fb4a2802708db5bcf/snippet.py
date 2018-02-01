import os

matrix = [
	[" ", " ", " "],
	[" ", " ", " "],
	[" ", " ", " "]
]
keymap = [
	"Q", "W", "E",
	"A", "S", "D",
	"Z", "X", "C"
]
matmap = [
	[0, 0], [0, 1], [0, 2],
	[1, 0], [1, 1], [1, 2],
	[2, 0], [2, 1], [2, 2]
]

game_over = 0
winner = ""
turn = 0

# Prints out title bar
def title():
	print("|-------------|")
	print("| Tic Tac Toe |")
	print("|-------------|")

# Prints out the grid
def grid(a, b, c, d, e, f, g, h, i):
	print("|             |")
	print("|    " + a + " " + b + " " + c + "    |")
	print("|    " + d + " " + e + " " + f + "    |")
	print("|    " + g + " " + h + " " + i + "    |")
	print("|             |")
	print("|-------------|")

# Prints out the matrix data as grid
def m2g():
	m = matrix
	grid(m[0][0], m[0][1], m[0][2],
		m[1][0], m[1][1], m[1][2],
		m[2][0], m[2][1], m[2][2])

# Print out keymappings
def tutorial():
	k = keymap
	os.system("clear")
	title()
	grid(k[0], k[1], k[2], k[3], k[4], k[5], k[6], k[7], k[8])
	print("Press ENTER to play")
	raw_input()

# Parses player input and does move
def parseInput(chr):
	for i in range(0, 9):
		if keymap[i] == chr:
			mloc = matmap[i]
			if matrix[mloc[0]][mloc[1]] == " ":
				matrix[mloc[0]][mloc[1]] = "X"
				return 1
			else:
				return -1
	return -2

# Finds an empty spot in the grid
def findEmpty(rcd, n):
	# Rows
	if rcd == "r":
		for x in range(3):
			if matrix[n][x] == " ":
				return x
	# Columns
	if rcd == "c":
		for x in range(3):
			if matrix[x][n] == " ":
				return x
	# Diagonals
	if rcd == "d":
		if n == 0:
			for x in range(3):
				if matrix[x][x] == " ":
					return x
		else:
			for x in range(3):
				if matrix[x][2-x] == " ":
					return x
	
	return -1

# Search for streaks number of X's or O's in a row/col/diagonal
def findStreaks(xo):
	m = matrix
	row = [0, 0, 0]
	col = [0, 0, 0]
	dia = [0, 0]
	
	# Check rows and columns for X streaks
	for y in range(3):
		for x in range(3):
			if m[y][x] == xo:
				row[y] += 1
				col[x] += 1
				
				#if row[y] == 3 or col[x] == 3:
				#	game_over = 1
				#	return
	
	# Check diagonals
	if m[0][0] == xo:
		dia[0] += 1
	if m[1][1] == xo:
		dia[0] += 1
		dia[1] += 1
	if m[2][2] == xo:
		dia[0] += 1
	if m[2][0] == xo:
		dia[1] += 1
	if m[0][2] == xo:
		dia[1] += 1
		
	return (row, col, dia)

# Finds the row/col/diagonal closest to winning
def aiThink():
	m = matrix
	
	row, col, dia = findStreaks("X")
	r, c, d = findStreaks("O")
	
	# Do move
	if aiMove(2, m, r, c, d) == 0:
		if aiMove(2, m, row, col, dia) == 0:
			if aiMove(1, m, r, c, d) == 0:
				aiMove(1, m, row, col, dia)

# Places an O at said winning row
def aiMove(n, m, row, col, dia):	
	for r in range(3):
		if row[r] == n:
			x = findEmpty("r", r)
			if x != -1:
				m[r][x] = "O"
				return 1
		if col[r] == n:
			y = findEmpty("c", r)
			if y != -1:
				m[y][r] = "O"
				return 1
	
	if dia[0] == n:
		y = findEmpty("d", 0)
		if y != -1:
			m[y][y] = "O"
			return 1
	if dia[1] == n:
		y = findEmpty("d", 1)
		if y != -1:
			m[y][2-y] = "O"
			return 1
	
	return 0

# Checks if specified player has won
def checkWin(xo):
	row, col, dia = findStreaks(xo)
	dia.append(0)
	
	for i in range(3):
		if row[i] == 3 or col[i] == 3 or dia[i] == 3:
			return 1
	
	return 0

def checkDraw():
	n = 0
	for y in range(3):
		for x in range(3):
			if matrix[y][x] != " ": n += 1
			
	if n == 9: return 1
	return 0

# Prints the stuff to the screen
def draw():
	os.system("clear")
	title()
	m2g()

# Initialize game
def init():
	game_over = 0
	winner = ""
	turn = 0
	
	tutorial()
	
	while game_over == 0:
		draw()
		
		print("    Turn  " + str(turn))
		
		i = raw_input("X> ").upper()
		if parseInput(i) == 1:
			turn += 1
			
			if checkWin("X") == 1:
				game_over = 1
				winner = "X"
			elif checkWin("O") == 1:
				game_over = 1
				winner = "O"
			elif checkDraw() == 1:
				game_over = 1
				winner = " "
				
			if game_over == 1:
				break
			
			aiThink()
			turn += 1
			
		if checkWin("X") == 1:
			game_over = 1
			winner = "X"
		elif checkWin("O") == 1:
			game_over = 1
			winner = "O"
		elif checkDraw() == 1:
			game_over = 1
			winner = " "
			
		if game_over == 1:
			break
					
	draw()
	w = winner + " Wins!" if winner != " " else " Draw! "
	print("|  Game Over  |")
	print("|   " + w + "   |")
	print("|-------------|")

init()
