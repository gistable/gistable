#!/usr/bin/env python3
# Usbourne Computer Space Games was a type-in computer games book 
# from the 1980s.   This is a version of "Moonlander" game.   
# Original BASIC  by Daniel Isaaman and Jenny Tyler

from time import sleep
print(chr(27) + "[2J")          # Clear screen
print("Moonlander")

                                #Set the starting values
time,height,velocity,fuel = 0,500,50,120

while True:
                                #print the values for height etc.
    print("Time {} Height {}".format(time,height))
    print("Vel  {} Fuel   {}".format(velocity,fuel))
    print("|"," "*(int(height*70/500)),"#",sep="")
    #if there is fuel left, it skips the part asking
    #how much to burn
    if fuel>0:
        #gets a number from you for the amount of fuel 
        #to burn, and checks if it is within limits
        try:
            burn = int(input("Burn :"))
        except ValueError:
            burn = 0
        if burn<0 : burn=0
        if burn>30 : burn=30
        if burn>fuel : burn = fuel
    else:
        sleep(1)
        burn = 0
    #calculate the new speed
    v1 = velocity - burn + 5
    #calculate new fuel level
    fuel -= burn
    #break out of the loop if it brings you to ground level
    if (velocity+v1)/2 >= height :
        break
    #calculate new speed
    height -= (velocity+v1)/2
    # increments time
    time += 1
    #update velocity
    velocity = v1

#calculates speed on touch down
v1 = int(velocity + (5-burn)*height/velocity)


if v1 >50:
    print("You made a new crater")
    print ("Impact velocity",v1)
if v1 > 5:
    print("You crashed. All are dead.")
    print ("Impact velocity",v1)
elif v1>1:
    print("Ok, but some injuries")
    print ("Landing velocity",v1)
else:
    print("Safe landing")
    print ("Landing velocity",v1)