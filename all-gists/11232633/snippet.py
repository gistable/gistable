import os
from time import sleep

Kaitlin = "Awesome!"

# made with love by Lindsay
print "Thank you Kaitlin!"
sleep(1)
print "for teaching us useful things like..."
sleep(1)

a = """  
         0
        \||
         /\ """

b = """  
         0
        ~|/
         /\ """
c = """  
         0
        -|/
        -\ """
d = """  

         0--|--==
       """
e = """  
         0
        \|/
         |\ """
f = """  
         0
        \|/
        /\ """
g = """  
        \/
        \|/
         0 """

dance_moves = [a, b, c, d, e, f, g, a, f, a, d, g, b]

def winning():
    print "Happy Dance!"
    sleep(.5)
    os.system('clear')
    for move in dance_moves:
        print move
        sleep(.5)
        os.system('clear')

winning()
print "Ok, maybe that is not the MOST useful thing you taught us, but it might be the most fun!\n"
sleep(1)

## Will Kaitlin read the source code?
## Of course one of Washington's top 50 women in tech will read the source code!


#for Kaitlin from Alisha 
message = "Kaitlin, thank you for teaching us Python!"
response = raw_input("Do you know how grateful we are?")
answer = "yes"
while response != answer:
    print "Aww, come on, we are SO grateful! So grateful that we actually did our final homework assignment, which is showing you how grateful we are." 
    response = raw_input("Try again. Do you know how grateful we are?")
print "We are eternally grateful! We love code so much we even do our homework now!" 

print
sleep(2)

# This is from former pupil Kat Lucero
x=[1,2,3,4,5,6,7,8]
for n in x:
    print "thanks kaitlin"

print

sleep(1)

# Olivia's wonderful script
welcomeNote = "Hey! Let's play a quick game of Mad Libs! \n"

print welcomeNote

adj =  raw_input("Enter an adjective: ")
feeling = raw_input("Enter a feeling: ")
noun = raw_input("Enter a noun: ")
verb = raw_input("Enter a verb: ")
animal = raw_input("Enter an animal: ")
place = raw_input("Enter a place: ")

print "\n Hi Kaitlin! \n We're super thankful " + feeling + " that you took the time to teach us how to code " + adj + "ly."
print "You're the best teacher ever! Even " + animal +"s could learn to code from you!"
print "We'll probably use our " + adj + " Python skills to make " + noun +"s " + verb + " all the time at " + place + "."
print "Thank you!"

print
if Kaitlin == "Awesome!":
    # allow awesome people to enjoy Olivia's script longer
    sleep(3)

# Contributed by one of Sunlight's star reporters, Peter 
bye = "Thank you for introducing us to Python! \n"

print bye

print "starts with \"L\" and rhymes with \"ducky\""
lucky = raw_input()

print "starts with \"gr-\" and rhymes with \"meaner\""
greener = raw_input()

print "We really appreciate your help teaching us to use Python. We were %s to have you helping us. I hope you enjoy your move to %s pastures. \n" % (lucky, greener)
print "Stay in touch!" 

print
sleep(2)

# This truth is brought to you by Kathy Kiely 
print "Leaving is futile. Your PyBabies will find you!!"

print
sleep(1)

# The contribution from the wonderful Rebecca Williams
message = "Kaitlin, You are the best and Rebecca is going to miss you SO INFINITELY MUCH."
question = raw_input("Kaitlin, do you want to know how Rebecca feels about your departure? ")
answer = "YES"
while question != answer:
	question = raw_input("Come on, you want to see this script do its magic. Let's try one more time where you say YES. Kaitlin, do you want to know how Rebecca feels about your departure? ")
while question == answer:
		print message 