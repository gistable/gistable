import random
import math

def cs16():    
    with open('CS16spread.csv', 'w') as file:
        i = 0
        file.write("x" + "," + "y" + "\n")
        
        
        while i < 100000:
            x = random.uniform(-0.5, 0.5) + random.uniform(-0.5, 0.5)
            y = random.uniform(-0.5, 0.5) + random.uniform(-0.5, 0.5)
            
            file.write(str(x) + "," + str(y) + "\n")
            i += 1


def csgo():            
    with open('CSgopolar.csv', 'w') as file:
        i = 0
        file.write("x" + "," + "y" + "\n")
        
        while i < 100000:
            theta = 2 * math.pi * random.uniform(0,1)
            r = random.uniform(-1, 1)
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            
            file.write(str(x) + "," + str(y) + "\n")
            i += 1
 
cs16()
csgo()