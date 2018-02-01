# La Sera is lost in the venue on the way to the stage!

from sys import exit
from random import randint

rock_of_ages = 0

# Scene's dont do much in this game, but you still have to set it up
class Scene(object):
	def enter(self):
		print "This scene is not yet configured."
		exit(1)
		
# creating the engine to run the game


class Engine(object):

	
	# you start game by entering scene_map (in this case, a_map)
	def __init__(self, scene_map):
		self.scene_map = scene_map
		
	
	
		
	def play(self):
		# goes to maps: calls opening_scene function, runs next_scene 
		# function, goes back to opening scene function, spits out
		# name of the opening room (ex: BackAlley)	
		current_scene = self.scene_map.opening_scene()
		
		
		# I just set the LAST scene to EchoStage
		# running next_scene on 'echostage' returns EchoStage
		last_scene = self.scene_map.next_scene('echostage')
		
		# this moves us from room to room
		# unless you are about to enter the last room, then it jumps
		# to the current_scene.enter() at the bottom
		
		while current_scene != last_scene:
			
			
			# runs enter on current_scene, returns whatever that room
			# says to return at the end (if youre in BackAlley,
			# it returns 'echoplex'
			next_scene_name = current_scene.enter()
			
			
			
			# this transforms room name KEY into room name VALUE
			# ex: if next_scene_name is 'echoplex', it returns EchoPlex
			current_scene = self.scene_map.next_scene(next_scene_name)
		
		
		# be sure to print out the last scene
		# this one only runs for the very last scene
		current_scene.enter()

	
	
class BackAlley(Scene):
	
	def enter(self):
		global rock_of_ages
		print "It's a hot summer night in Los Angeles..."
		pause = raw_input("*** (hit enter) ***")
		print "You just got hired as La Sera's new theremin player, you crazy shredding animal"
		pause = raw_input("***")
		print "No one knew a theremin could be played with such passion, until you arrived."
		pause = raw_input("***")
		print "Tonight is the night, your first show with the band.  It's at The Echo,"
		print "our very favorite venue in Los Angeles."
		pause = raw_input("***")		
		print "But the layout can be pretty confusing..."
		print "There's a big venue downstairs called The Echoplex"
		pause = raw_input("***")
		print "There's a back patio, a pizza place next door,"
		print "crowds of people everywhere, aliens, all sorts of stuff."
		pause = raw_input("***")
		print " !!! A ROAR OF APPLAUSE EXPLODES IN THE BACKGROUND !!! "
		pause = raw_input("***")
		print "OH SHIT! SPRINGTIME CARNIVORE JUST FINISHED THEIR WONDERFUL SET!"
		pause = raw_input("***")
		print "GET US TO THE STAGE! WE HAVE TO PLAY IN 15 MINUTES!"
		pause = raw_input("***")
		print "Right now, we are in the alley behind the venue..."
		print "Do we run into this door here in front of us?"
		print "Or go up the hill to the back patio?!"
		
		
		x = 0
		while x == 0:
			choice = raw_input("Type DOOR or PATIO > ")
			if choice == 'DOOR' or choice == 'door':
				x = 1
			 	return 'echoplex'
			elif choice == 'PATIO' or choice == 'patio':
				x = 1
				return 'backpatio'
			elif choice == "secret alien room" or choice == "SECRET ALIEN ROOM":
				return 'secretalienroom'
			else:
				print "That's not an option, idiot!"
			

class Echoplex(Scene):
	def enter(self):
		global rock_of_ages
		
		print "We are now in a dark, foggy room. Maybe it's an underground lair?"
		pause = raw_input("***")
		print "\"No.  It is...The Echoplex\" said a voice from the darkness"
		pause = raw_input("***")
		print "\"Nobunny!?  Is that you??\" we all ask in unison..."
		pause = raw_input("***")
		print "\"Hey guys!  Yeah I'm playing here tonight!  What's going on?!\""
		pause = raw_input("***")
		print "\"Well Nobunny, we are actually lost!"
		print "We are supposed to play upstairs in 5 minutes!\""
		pause = raw_input("***")
		print "\"Can you help us??\""
		pause = raw_input("***")
		print "\"I'm glad you asked.\" said Nobunny."
		print "He then pulled out a mysterious object from his pocket."
		pause = raw_input("***")
		print "\"This is the 'Rock of Ages'.  It knows all."
		print "If you guess it's favorite number, I can help you.  You have 3 tries."
		pause = raw_input("***")
		print "You must guess the number! Fast! It's a number between 1 and 10..."
		
		number = str(randint(1,9))
		
		guess_count = 0
		
		guess = raw_input("Enter number > ")
		
		while guess != number and guess_count < 10:
			guess_count += 1
			print "No!  That's not right! Guess again!" 
			
			
			guess = raw_input("Enter number > ")
			
		
		if guess == number:
			print "You did it!  Great job, for a theremin player..."
			pause = raw_input("***")
			print "\"Ok just go back out the way you came..."
			pause = raw_input("***")
			print "\"Make a left and go around to the back patio!\""
			pause = raw_input("***")
			print "\"And here! Take the 'Rock of Ages'! You might need it...\""
			rock_of_ages = 1
			pause = raw_input("***")
			print "You tell Nobunny to have a great show tonight and you lead the way..."
			pause = raw_input("***")
			return 'backpatio'
		else:
			print "You have angered the 'Rock of Ages'!"
			pause = raw_input("***")
			print "Now are ALL going to die!"
			pause = raw_input("***")
			print "THE END"
			pause = raw_input("***")
			exit(1)
				

class BackPatio(Scene):
	def enter(self):
		global rock_of_ages
		print "This is looking promising!"
		pause = raw_input("***")
		print "Why is the patio so empty?"
		pause = raw_input("***")
		print "What is that faint glowing by the trashcan?"
		pause = raw_input("***")
		print "As you approach what you ASSUME to be a cigarette butt..."
		pause = raw_input("***")
		print "The glowing embers intensify, and begin to levitate upwards..."
		pause = raw_input("***")
		print "The floating orb then begins to YELL"
		pause = raw_input("***")
		print "\"PAUSE EARTHLING! YOU MAY NOT PASS! EXTEEEERMINATE!\""
		pause = raw_input("***")
		print "Holy shit what have you done?! Get us out of here!"
		pause = raw_input("***")
		print "Do you... fight the alien? Or run away fast!"
		
		choice = raw_input("FIGHT or RUN? > ")
		count = 0
		while count == 0:
			if choice == "FIGHT" or choice == "fight" or choice == "Fight":
				count += 1
				print "YOU STUPID, EGOTISTICAL, THEREMIN-LOVING FOOL"
				pause = raw_input("***")
				print "GALACTIC PIRATE KILLERS HAVE INVADED OUR BODIES"
				pause = raw_input("***")
				print "Now...even if we MAKE IT to the show...we will only know one song!"
				pause = raw_input("***")				
				print "The Intergalactic Song of the Overlord Armies"
				pause = raw_input("***")
				print "And no one wants to hear that.  No one!"
				pause = raw_input("***")
				print "This band is OVER! And we probably die, too"
				pause = raw_input("***")
				print rock_of_ages
				if rock_of_ages == 1:
					print "Wait! Not all hope is lost!"
					pause = raw_input("***")
					print "You still have the 'Rock of Ages', yes?"
					pause = raw_input("***")
					print "We are saved!"
					pause = raw_input("***")
					print "You throw the 'Rock of Ages' into the cloudy belly of the beast."
					pause = raw_input("***")
					print "And we run as fast as we can towards the nearest door and stumble into..."
					pause = raw_input("***")
					print "a kitchen?"
					pause = raw_input("***")
					rock_of_ages = 2
					
					return 'twoboots'
				else:
					print "THE END"
					pause = raw_input("***")
					exit(1)
			elif choice == "RUN" or choice == "run" or choice == "Run":
				count += 1
				print "Quick! This way!"
				pause = raw_input("***")
				print "We all run towards the nearest door and stumble into..."
				pause = raw_input("***")
				print "a kitchen?"
				pause = raw_input("***")
				return 'twoboots'
			else:
				print "Don't just stand there! Fight or run!"
				choice = raw_input("FIGHT or RUN? > ")
				
			
		
		
		
class TwoBoots(Scene):
	def enter(self):
		print "Here we are in the kitchen of Two Boots pizza!"
		pause = raw_input("***")
		print "The pizza place NEXT DOOR to The Echo..."
		pause = raw_input("***")
		print "We all love pizza as much as the next band,"
		pause = raw_input("***")
		print "But we have a SHOW to play!"
		pause = raw_input("***")
		print "You look up and see something strange... a very high ponytail."
		pause = raw_input("***")
		print "You look to the left and see ANOTHER high ponytail."
		pause = raw_input("***")
		print "What is going on in here?!"
		pause = raw_input("***")
		print "\"You are in OUR HOUSE now!\""
		pause = raw_input("***")
		print "Jenny Lewis?! Why are you in here making pizza?!"
		pause = raw_input("***")
		print "\"This isn't just ANY pizza.  This is ponytail pizza."
		pause = raw_input("***")
		print "The second girl then turns around...Katie Crutchfield?!"
		pause = raw_input("***")
		print "\"Hey guys!\""
		pause = raw_input("***")
		print "Jenny Lewis, Liz Pelly and I are just here making our signature ponytail pizza!\""
		pause = raw_input("***")
		print " ... "
		pause = raw_input("***")
		print " ... ..."
		pause = raw_input("***")
		print "Um, that is NOT a thing.  Definitely not a thing."
		pause = raw_input("***")
		print "Is that a thing?!?!"
		
		choice = raw_input("Yes or No? > ")
		count = 0
		while count == 0:
			if choice == "Yes" or choice == "YES" or choice == "yes":
				count += 1
				print "Well alright then!  By the way, can you help us?"
				pause = raw_input("***")
				print "We need to get to The Echo ASAP! We play in 5 min!"
				pause = raw_input("***")
				print "\"Sure, we can help!\""
				pause = raw_input("***")
				print "And with a quick whip of their ponytails, all became clear."
				pause = raw_input("***")
				print "You quickly acheieve all of the clairvoyance of a god."
				pause = raw_input("***")
				print "All of time and space becomes 1s and 0s, like in that part in The Matrix."
				pause = raw_input("***")
				print "You say \"I know where to go.\" And we know this to be true."
				pause = raw_input("***")
				
				return 'frontlobby'
				
			elif choice == "No" or choice == "NO" or choice == "no":
				count += 1
				print "A wave of anger washes over the kitchen."
				pause = raw_input("***")
				print "Eyes red with fury, mouths foaming with rage..."
				pause = raw_input("***")
				print "Their high ponytails begin whipping in circles with such velocity..."
				pause = raw_input("***")
				print "That the space-time continuum begins to tear from within..."
				pause = raw_input("***")
				print "Suddenly, the face of Ariana Grande appears amidst the chaos"
				pause = raw_input("***")
				print "And as you look into her smoldering eyes..."
				pause = raw_input("***")
				print "the blackhole spaghettifies you into a human noodle."
				pause = raw_input("***")
				print "THE END!"
				pause = raw_input("***")
				exit(1)
			else:
				print "That's not a choice. Try again."
				choice = raw_input("Yes or No? > ")
		
		
		
class FrontLobby(Scene):
	def enter(self):
		global rock_of_ages
		print "Whew that was a close one!"
		pause = raw_input("***")
		print "Are you eating that weird ass pizza?"
		pause = raw_input("***")
		print "Never mind, we don't care.  Eat away."
		pause = raw_input("***")
		print "We run out onto Sunset Blvd.  We did it! There's The Echo!"
		pause = raw_input("***")
		print "You walk in the front doors and are greeted by the sweet sound of..."
		pause = raw_input("***")
		print "\"DEATH TO YOU!!!!\" OH GOD IT'S THE FLOAT-Y ORB-Y ALIEN!"
		pause = raw_input("***")
		print "How did it get here so fast?!"
		pause = raw_input("***")
		print "\"STUPID HUMAN. YOU FORGOT ABOUT THE BACK DOOR OF THE ECHO!\""
		pause = raw_input("***")
		print "\"YOU MISSED YOUR CHANCE TO PLAY THE SHOW.\""
		pause = raw_input("***")
		print "\"YOU HAVE TWO CHOICES.  YOU CAN DIE!!!! OR...\""
		pause = raw_input("***")
		print "\"You are free to walk down these stairs to the right and go watch Nobunny play.\""
		pause = raw_input("***")
		print "\"Either option is cool by me, mmhmm. I am an alien yup yup yup...\""
		pause = raw_input("***")
		print "Hmm. This is it, you guys.  Our final hurdle. Our last hoorah."
		pause = raw_input("***")
		print "The people in there are chanting our name."
		pause = raw_input("***")
		print "\"LA-SE-RA! LA-SE-RA!\" You can hear the people getting crazy."
		pause = raw_input("***")
		if rock_of_ages == 0:
			print "\"YOU HAVE NO POWER HERE, HUMANS. I SEE NO MAGICAL DEFENSIVE WEAPONS.\""
			pause = raw_input("***")
			print "\"YOU, QUITE TRULY, ARE F*CKED.\""
			pause = raw_input("***")
			print "What are we going to do?"
			pause = raw_input("***")
			choice = raw_input("Nobunny or Die? >")
			
			if choice == "Nobunny" or choice == "NOBUNNY" or choice == "nobunny":
				print "That'll do, pig.  That'll do."
				pause = raw_input("***")
				print "We go downstairs and watch Nobunny."
				pause = raw_input("***")
				print "He actually asks you to come up on stage and play guest theremin."
				pause = raw_input("***")
				print "Who would've thought?"
				pause = raw_input("***")
				print "THE END!"
				pause = raw_input("***")
				exit(1)
			elif choice == "SECRET ALIEN ROOM" or choice == "secret alien room":
				return 'secretalienroom'
			else:
				print "With a blinding flash of light, the alien uses it's laser powers..."
				pause = raw_input("***")
				print "To instantly slice all of our bodies into 1000 pieces."
				pause = raw_input("***")
				print "THE END!"
				pause = raw_input("***")
				exit(1)
				
					
		elif rock_of_ages == 1:
			print "The 'Rock of Ages'!  I knew this would come in handy!"
			pause = raw_input("***")
			print "You throw the 'Rock of Ages' directly into the amorphous alien blob."
			pause = raw_input("***")
			print "He explodes into a trillion memories!"
			pause = raw_input("***")
			print "You watch as all that was and all that will be crashes around you"
			pause = raw_input("***")
			print "Like the rain of a thousand suns."
			pause = raw_input("***")
			print "TIME TO ROCK! We barge through the doors..."
			pause = raw_input("***")
			return 'echostage'		
		elif rock_of_ages == 2:
			print "God damn you, Theremin Child, you already used the 'Rock of Ages'!"
			pause = raw_input("***")
			print "You had ONE JOB.  And that was to save us from alien attacks! And play theremin."
			pause = raw_input("***")
			print "Let's go watch Nobunny play and have a fucking ball!"
			pause = raw_input("***")
			print "We go downstairs and to the Nobunny show"
			pause = raw_input("***")
			print "He actually asks you to come up on stage and play guest theremin."
			pause = raw_input("***")
			print "Who would've thought?"
			pause = raw_input("***")
			print "THE END!"
			pause = raw_input("***")
			exit(1)
		else:
			print "NOT AN OPTION! DIE DIE DIE!"
			pause = raw_input("***")
			print "THE END!"
			exit(1)
			
			
	
class SecretAlienRoom(Scene):
	def enter(self):
		print """
		    WELCOME TO THE SECRET ALIEN ROOM
	WHERE ALL OF YOUR SECRET ALIEN FANTASTIES COME TRUE
	    WE ARE ALL FRIENDS IN THE SECRET ALIEN ROOM
	      AND WE ARE ALL ONE.  ALL ONE.  ALL ONE.
		"""
		pause = raw_input("***")
		print """		       
		  NO ONE ESCAPES THE SECRET ALIEN ROOM
	        IT JUST GOES ON AND ON AND ON
		        FOR ALL OF ETERNITY.  
		    OR MAYBE JUST A BLINK OF THE EYE?
		         WHO IS TO SAY?  NOT I.
		 """
		pause = raw_input("***")
		print """
			  FOR WHO AM I BUT A SERVANT
			A MASTER OF TRICKERY ALL ALONG!
			  SO GO ON, MY MUSICAL BEASTS
		  AND LET THE CHILDREN HEAR YOUR SONG
		"""
		pause = raw_input("***")
		return 'echostage'

		
class EchoStage(Scene):
	def enter(self):
		
		print "At last! We made it! We immediately jump right into our set"
		pause = raw_input("***")
		print "Everyone is stoked.  The universe makes sense again."
		pause = raw_input("***")
		print "Or does it?"
		pause = raw_input("***")
		print "YOU WIN! For now..."
		pause = raw_input("***")
		print "THE END!"
		exit(1)
	
	
class Map(object):
	
	
	scenes = {
		'backalley': BackAlley(),
		'backpatio': BackPatio(),
		'echoplex': Echoplex(),
		'twoboots': TwoBoots(),
		'secretalienroom': SecretAlienRoom(),
		'frontlobby': FrontLobby(),
		'echostage': EchoStage(),
	}
	
	# defines a_map as a map with 'backalley' as start_scene
	def __init__(self, start_scene):
		self.start_scene = start_scene
	
	# given scene_name key, it returns VALUE (BackAlley)
	def next_scene(self, scene_name):
		val = Map.scenes.get(scene_name)

		return val
	
	def opening_scene(self):
								#'backalley'
				# (							) = BackAlley
		return self.next_scene(self.start_scene)
				
a_map = Map('backalley')

a_game = Engine(a_map)
a_game.play()
