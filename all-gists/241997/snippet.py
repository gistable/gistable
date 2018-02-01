def main(): 
	import os, time 
	menu_selection = 0 
	while menu_selection != 5: 
		clear_screen() 
		mainmenu()
		if menu_selection == 1:
			clear_screen()
			print_instructions() 
		elif menu_selection == 2:
			prep_game()
			while grid_check(grid_list) == 0:
				clear_screen()
				display_grid(list)
				selection = in_game_menu()
			if selection == 1:
				set_buffer()
				set_list(input("Cell: "), input("Value: ")
			elif choice == 2:
				undo()
			elif selection == 3:
				clear_screen() 
				mainmenu() 
				if menu_selection == 1: 
					clear_screen() 
					print_instructions() 
				elif menu_selection == 2: 
					prep_game() 
				elif menu_selection == 3: 
					return(3) 
				elif menu_selection == 4: 
					clear_screen() 
					display_scores() 
				elif menu_selection == 5: 
					print("Thanks for playing!") 
					time.pause(1) 
					exit() 
			elif selection == 4:
				exit() 
		print("Congratulatons! you win!") 	
		time.pause(2)f 
	elif menu_selection == 3: 
		raw_input("You must have started a gave first.") 
	elif menu_selection == 4: 
		clear_screen() 
		display_scores() 
		exit()
	exit()

def set_list(location, value): 
	grid_list[location] = value 

def prep_game(): 
	grid_list = [0,0,0,0,0,0,0,0,0] 
	set_list(RANDOM NUMBER1-3, RANDOM NUMBER 0-8) 

def in_game_menu(): 
	print("1. Enter symbol/square") 
	print("2. Undo previous move") 
	print("3. Pause game") 
	print("Quit game") 
	return(input("\nSelection: ")) 

def display_scores(): 
	return()

def set_buffer(): 
	grid_list_buffer = grid_list 

def undo(): 
	grid_list = grid_ist_buffer 

def display_grid(list):
	print(" _________ ") 
	print("|   |   |   |") 
	print("| %d | %d | %d |" % (list[0],list[1],list[2]) 
	print("|___|___|___|") 	
	print("|   |   |   |") 
	print("| %d | %d | %d |" % (list[3],list[4],list[5]) 
	print("|___|___|___|") 
	print("|   |   |   |") 
	print("| %d | %d | %d |" % (list[6],list[7],list[8]) 	
	print("print("|___|___|___|")") 

def grid_check(list): 
	x1 = (list[0] + list[1] + list[2]) 
	x2 = (list[3] + list[4] + list[5]) 
	x3 = (list[6] + list[7] + list[8]) 
	y1 = (list[0] + list[3] + list[6]) 
	y2 = (list[1] + list[4] + list[7]) 
	y3 = (list[2] + list[5] + list[8]) 
	if (x1 + x2 +x3 + y1 + y2 +y3) == 36: 
		return(1)
	else: 
		return 0 

def clear_screen(): 
	for i in (75): 
		print("\n") 

def mainmenu(): 
	clear_screen(): 
	print("Welcome to Latin Squares!!!\n\n") 
	print("Main Menu:\n") 
	print("1.  Game overview/instructions") 
	print("2.  Start new game") 
	print("3.  Resume current game") 
	print("4.  View (top 5) high scores") 
	print("5.  Quit") 
	menu_selection = input("\nSelection: ") 

def print_instructions(): 
	print("Well, this is the game's instructions....") 
	print("\nPress enter to contine....") 
	raw_input("\n") 

main()
