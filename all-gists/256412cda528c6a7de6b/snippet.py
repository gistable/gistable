""" rock paper scissors lizard spock
		
		Scissors cuts Paper
		Paper covers Rock
		Rock squishes Lizard
		Lizard poisons Spock
		Spock dismantles Scissors
		Scissors decapitates Lizard
		Lizard eats Paper
		Paper disproves Spock
		Spock vaporizes Rock
		(and as it always has) Rock crushes scissors
		
		john coyne
		feb 11 2015 """
		
import random
		
def playRPSLS(aPlayer,a,bPlayer,b,elements):
	
	if a == b:
		winner = 'nobody'
		winnerPlayer = a
		action = 'ties'
		loserPlayer = b
		
	else:
		
		for element in elements:
			if a == element[0]:
				aName = element[1]
				for t in element[2]:
					if t == b:
						winner = aPlayer
						winnerPlayer = aName
						action = element[2][t]
						
		for element2 in elements:
			if b == element2[0]:
				bName = element2[1]
				for t in element2[2]:
					if t == a:
						winner = bPlayer
						winnerPlayer = bName
						action = element2[2][t]
	
		if winner == aPlayer:
			loserPlayer = bName
		else:
			loserPlayer = aName
						
	return (winner,winnerPlayer,action,loserPlayer)

choices = [('r','rock',({'s':'crushes','l':'squishes'})),
           ('p','paper',({'r':'covers','k':'disproves'})),
           ('s','scissors',({'p':'cuts','l':'decapitates'})),
           ('l','lizard',({'p':'eats','k':'poisons'})),
           ('k','spock',({'s':'dismantles','r':'vaporizes'})),
           ] # id, name, what it beats

choiceCount = len(choices)

userChoice = raw_input('choose (r)ock (p)aper (s)cissors (l)izard spoc(k): ')

computerRand = random.randint(0,choiceCount-1)
computerChoice = choices[computerRand][0]

result = playRPSLS('user',userChoice,'computer',computerChoice,choices)

print('computer played {0}, user played {1}'.format(computerChoice,userChoice))

print('{0} won! {1} {2} {3}\n'.format(result[0],result[1],result[2],result[3]))


