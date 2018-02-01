import random 
import string
# -*- coding: utf-8 -*-


def randomname(length = 6):
	vowels = ['a','e','i','o','u','']
	consonants = ['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','y','z'] 
	a = random.sample(consonants,length/2)
	x = 1
	while x < length:
		a.insert(x,random.choice(vowels))
		x = x+2
	return "".join(a).title()


def randomshape(length = 6):
	vowels = ['_', '_']
	consonants = ['|','_','_','_','_','_','.','[',']','|','_','_','_','_','_','.','_','_','|','_','_','_','_','_','.','_','_','|','_','_','_','_','_','.','[',']','|','_','_','_','_','_','.','_','_','|','_','_','_','_','_','.','_','_','|','_','_','_','_','_','.','[',']','|','_','_','_','_','_','.','_','_','|','_','_','_','_','_','.','_','_'] 
	a = random.sample(consonants,length/2)
	x = 1
	while len(a) < length:
		a.insert(x,random.choice(vowels))
		x = x+2
	return "".join(a).title()




def id_generator(size=6, chars=string.ascii_letters + "-_:|!"):
	return ''.join(random.choice(chars) for _ in range(size))

albumtitle = randomname(8)

score = open(albumtitle +".txt", 'a')

mood = [
'Accepted',
'Accomplished',
'Aggravated',
'Alone',
'Amused',
'Angry',
'Annoyed',
'Anxious',
'Apathetic',
'Apologetic',
'Ashamed',
'Awake',
'Bewildered',
'Bitchy',
'Bittersweet',
'Blah',
'Blank',
'Blissful',
'Bored',
'Bouncy',
'Brooding',
'Calm',
'Cautious',
'Chaotic',
'Cheerful',
'Chilled',
'Chipper',
'Cold',
'Complacent',
'Confused',
'Content',
'Cranky',
'Crappy',
'Crazy',
'Crushed',
'Curious',
'Cynical',
'Dark',
'Defensive',
'Delusional',
'Demented',
'Depressed',
'Determined',
'Devious',
'Dirty',
'Disappointed',
'Discontent',
'Ditzy',
'Dorky',
'Drained',
'Drunk',
'Ecstatic',
'Energetic',
'Enraged',
'Enthralled',
'Envious',
'Exanimate',
'Excited',
'Exhausted',
'Fearful',
'Flirty',
'Forgetful',
'Frustrated',
'Full',
'Geeky',
'Giddy',
'Giggly',
'Gloomy',
'Good',
'Grateful',
'Groggy',
'Grumpy',
'Guilty',
'Happy',
'Heartbroken',
'High',
'Hopeful',
'Hot',
'Hungry',
'Hyper',
'Impressed',
'Indescribable',
'Indifferent',
'Infuriated',
'Irate',
'Irritated',
'Jealous',
'Joyful',
'Jubilant',
'Lazy',
'Lethargic',
'Listless',
'Lonely',
'Loved',
'Mad',
'Melancholy',
'Mellow',
'Mischievous',
'Moody',
'Morose',
'Naughty',
'Nerdy',
'Numb',
'Okay',
'Optimistic',
'Peaceful',
'Pessimistic',
'Pissed off',
'Pleased',
'Predatory',
'Quixotic',
'Rapturous',
'Recumbent',
'Refreshed',
'Rejected',
'Rejuvenated',
'Relaxed',
'Relieved',
'Restless',
'Rushed',
'Sad',
'Satisfied',
'Shocked',
'Sick',
'Silly',
'Sleepy',
'Smart',
'Stressed',
'Surprised',
'Sympathetic',
'Thankful',
'Tired',
'Touched',
'Uncomfortable',
'Weird'
]

source = [
'Voice sounds',
'Guitar sounds', 
'Drone sounds', 
'Drum loops', 
'Nature sounds',
'Piano sounds',
'Speech',
'Noise',
'None',
'None']

filter = [
'Bandpass', 
'Lowpass',
'Hipass',
'Notch',
'None',
'Chords',
'Sounds']

modulation = [
'Audio',
'Pings',
'Slow lfo',
'Sweep',
'None',
'Chords',
'Stepped']

slope = [
'envelope',
'looped',
'slow',
'fast',
'None']

resonance = [
'off',
'cusp',
'warm',
'extreme'
]

chords = [
'high',
'mid',
'low',
'odd',
'major',
'slow',
'fast',
'smooth',
'coarse',
'None',
'None']

sequence = [
'random',
'2',
'3',
'4',
'5',
'6',
'8',
'16',
'audio clocked',
'chord clocked',
'None',
'None']

score.write(albumtitle)
score.write("\r")

for count in albumtitle:
	score.write("-")
score.write("\r")
score.write("\r")

for x in range(1, random.randint(5, 12)):
	score.write("Track " + str(x) + ": " + randomname(random.randint(5,12)))
	score.write("\r")
	score.write("Mood: ")
	score.write(random.choice(mood))
	score.write(", ")
	score.write(random.choice(mood))
	score.write(".\r")
	score.write("Source: ")
	score.write(random.choice(source).title())
	score.write(".\r")	
	score.write("Filter: ")
	score.write(random.choice(filter).title())
	score.write(".\r")	
	score.write("Modulation: ")
	score.write(random.choice(modulation).title())
	score.write(".\r")
	score.write("Slope: ")
	score.write(random.choice(slope).title())
	score.write(".\r")	
	score.write("Resonance: ")
	score.write(random.choice(resonance).title())
	score.write(".\r")	
	score.write("Chords: ")
	score.write(random.choice(chords).title())
	score.write(".\r")	
	score.write("Sequence: ")
	score.write(random.choice(sequence).title())
	score.write(".\r")	
	
	score.write("\r")
	score.write("\r")

	height=random.randint(1, 12)
	width =random.randint(8, 64)
	for q in range(0,height):  
		score.write(randomshape(width) + '\r')

	score.write("\r\r")