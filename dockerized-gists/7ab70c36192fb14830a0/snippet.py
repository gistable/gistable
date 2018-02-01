def bisection():
	print("Please pick a number between 1 and 100!")
	ans = int(raw_input())
	assert 0<ans<=100 #raises a value error if too high or too low number is picked
	floor, ceiling, bisector = 1, 100, None 
	while bisector != ans:
		assert floor < 100 and ceiling < 101 #floor or ceiling too high
		bisector = (floor+ceiling)//2
		print('Is %s the number you picked? Say low if its too low, high if its too high, or correct if its the number you chose.') % (bisector)
		response = raw_input()
		if response == 'correct':
			break
		if response == 'low':
			floor = floor * (ceiling//2)
		if response == 'high':
			ceiling = ceiling//2
	print('So the number you chose is %s, isnt it? AHA! told you im fucking psychic :)') % (ans)
	
